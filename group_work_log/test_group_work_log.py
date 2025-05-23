import unittest
import requests
import subprocess
import time
import os
import json
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("group_work_log_test")

def server_is_running():
    """Prüft, ob der FastAPI-Server auf Port 8082 läuft"""
    try:
        response = requests.get("http://localhost:8082/summaries", timeout=1)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

class TestGroupWorkLogEndpoints(unittest.TestCase):
    """Testet die API-Endpunkte von group_work_log.py"""

    @classmethod
    def setUpClass(cls):
        """Setup vor allen Tests: Prüft, ob der Server läuft oder startet ihn"""
        cls.api_url = "http://localhost:8082"
        cls.server_process = None

        # Prüfen, ob der Server bereits läuft
        if not server_is_running():
            logger.info("Starting FastAPI server...")
            # Server im Hintergrund starten
            cls.server_process = subprocess.Popen(
                ["python", "group_work_log.py"]
            )

            # Warten bis Server bereit ist
            retries = 0
            max_retries = 15
            while retries < max_retries and not server_is_running():
                logger.info(f"Waiting for server (attempt {retries+1}/{max_retries})...")
                time.sleep(1)
                retries += 1

            if retries >= max_retries:
                logger.error("Server could not be started.")
                if cls.server_process:
                    cls.server_process.terminate()
                raise unittest.SkipTest("Server could not be started")

        logger.info("Server is running, tests can begin.")

        # Testdaten vorbereiten
        cls.prepare_test_data()

    @classmethod
    def tearDownClass(cls):
        """Cleanup nach allen Tests: Server beenden, wenn er von uns gestartet wurde"""
        if cls.server_process:
            logger.info("Shutting down server...")
            cls.server_process.terminate()
            try:
                cls.server_process.wait(timeout=5)
                logger.info("Server shut down successfully.")
            except subprocess.TimeoutExpired:
                logger.warning("Server not responding, forcing termination...")
                cls.server_process.kill()
                logger.info("Server forcefully terminated.")

    @classmethod
    def prepare_test_data(cls):
        """Testdaten für die API-Tests vorbereiten"""
        # Beispiel-Konversation wie vom Nutzer bereitgestellt
        cls.test_conversation = [
            {'role': 'user', 'content': 'What toolscan you6 use?'},
            {'role': 'assistant', 'content': [{'type': 'text', 'text': "I have access to the following tools:\n\n1. **read_file** - Read the contents of files, with optional line range selection\n2. **list_files** - List files and directories in a given path\n3. **edit_file** - Make edits to text files by replacing specific text\n4. **delete_file** - Delete files (cannot be undone)\n5. **git_command** - Execute git commands like add, commit, status, push, etc.\n6. **restart_program** - Restart the Python program while preserving conversation context\n7. **reset_context** - Reset conversation context by deleting saved context file\n8. **ask_human** - Request information or confirmation from you\n9. **calculator** - Perform mathematical calculations and evaluate expressions\n10. **create_tool** - Create new tools to enable additional capabilities I currently lack\n11. **send_group_message** - Send messages to a group chat of agents\n\nThese tools allow me to work with files, perform git operations, do calculations, communicate with you and other agents, and even create new tools when needed. Is there something specific you'd like me to help you with using any of these tools?"}]},
            {'role': 'user', 'content': "Can you create a simple tool printing 'Hello World' ?"},
            {'role': 'assistant', 'content': [{'type': 'text', 'text': "I'll create a simple tool that prints 'Hello World' for you."}, {'type': 'tool_use', 'id': 'toolu_01GAp8j3LEzEymoWhaBitJPa', 'name': 'create_tool', 'input': {'toolname': 'hello_world', 'description': "A simple tool that prints 'Hello World' to the console. This tool takes no parameters and simply outputs the classic greeting message."}}]},
            {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': 'toolu_01GLv87cv1TYjJbviBQcxSZa', 'content': 'Hello World'}]},
            {'role': 'assistant', 'content': [{'type': 'text', 'text': 'Excellent! The hello_world tool has been successfully created and is working perfectly. \n\nTo summarize what I did:\n1. Created a new tool file `tools/hello_world_tool.py` following the same pattern as other tools\n2. Added the import and tool definition to `tools/__init__.py`\n3. Updated `tools_utils.py` to import and include the HelloWorldDefinition in the tool list\n4. Restarted the program to load the new tool\n5. Successfully tested the tool\n\nThe hello_world tool is now available and ready to use whenever you need it! It takes no parameters and simply prints and returns "Hello World".'}]}
        ]

        # Testkonversation speichern für zukünftige Verwendung
        with open("test_conversation.json", "w", encoding="utf-8") as f:
            json.dump(cls.test_conversation, f, indent=2)

        # Basis-Timestamp für Tests
        cls.first_timestamp = "2025-05-23T12:21:44.335606"
        cls.last_timestamp = "2025-05-23T12:21:54.335606"

    def test_server_health(self):
        """Testet, ob der Server korrekt antwortet"""
        logger.info("Testing server health...")
        response = requests.get(f"{self.api_url}/summaries")
        self.assertEqual(response.status_code, 200, "Server should respond with HTTP 200")
        logger.info("Server health check passed.")

    def test_summarize_conversation_endpoint(self):
        """Testet den /summarize_conversation Endpunkt mit dem neuen Format"""
        logger.info("Testing /summarize_conversation endpoint with new format...")

        # Anfrage mit neuer Struktur senden
        agent_id = "agent-harry"
        logger.info(f"Sending conversation for agent: {agent_id}")
        response = requests.post(
            f"{self.api_url}/summarize_conversation",
            json={
                "agent_id": agent_id,
                "first_timestamp": self.first_timestamp,
                "last_timestamp": self.last_timestamp,
                "conversation": self.test_conversation
            }
        )

        # Prüfungen
        self.assertEqual(response.status_code, 200, "Endpoint should return HTTP 200")
        data = response.json()
        logger.info(f"Response received: {json.dumps(data, indent=2)}")

        self.assertEqual(data["status"], "ok", "Status should be 'ok'")
        self.assertTrue(data["summary_created"], "Summary should have been created")
        self.assertIn("summary_timestamp", data, "Response should contain a timestamp")

        # Warten, bis Zusammenfassung verarbeitet wurde
        logger.info("Waiting for summary to be processed...")
        time.sleep(1)

        # Prüfen, ob Zusammenfassung in Datei gespeichert wurde
        self.assertTrue(os.path.exists("agent_work_summaries.txt"),
                        "Summary file should exist")
        logger.info("Summary file exists.")

        # Dateiinhalt prüfen
        with open("agent_work_summaries.txt", "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"First 200 characters of the summary file:\n{content[:200]}...")
            self.assertIn(f"=== AGENT: {agent_id} ===", content,
                         "Summary should contain the agent name")
            self.assertIn("TIMESPAN:", content,
                         "Summary should contain timespan")
            self.assertIn(self.first_timestamp, content,
                         "Summary should contain first timestamp")
            self.assertIn(self.last_timestamp, content,
                         "Summary should contain last timestamp")
            self.assertIn("TOTAL STEPS:", content,
                         "Summary should contain step count")

        logger.info("Summarize conversation test passed.")

    def test_get_summaries_endpoint(self):
        """Testet den /summaries Endpunkt"""
        logger.info("Testing /summaries endpoint...")

        # Zusammenfassung mit eindeutigem Agenten erstellen
        unique_agent = f"test-agent-{datetime.now().timestamp()}"
        logger.info(f"Creating summary for unique agent: {unique_agent}")

        post_response = requests.post(
            f"{self.api_url}/summarize_conversation",
            json={
                "agent_id": unique_agent,
                "first_timestamp": self.first_timestamp,
                "last_timestamp": self.last_timestamp,
                "conversation": self.test_conversation
            }
        )

        self.assertEqual(post_response.status_code, 200, "Summary creation should succeed")
        timestamp = post_response.json()["summary_timestamp"]
        logger.info(f"Summary created with timestamp: {timestamp}")

        # Warten, bis Zusammenfassung verarbeitet wurde
        time.sleep(1)

        # Alle Zusammenfassungen abrufen
        logger.info("Retrieving all summaries...")
        all_summaries_response = requests.get(f"{self.api_url}/summaries")
        self.assertEqual(all_summaries_response.status_code, 200,
                        "Summaries endpoint should return HTTP 200")

        all_summaries = all_summaries_response.json()
        logger.info(f"Retrieved {len(all_summaries)} summaries")
        self.assertIsInstance(all_summaries, list, "Response should be a list")
        self.assertGreater(len(all_summaries), 0, "There should be at least one summary")

        # Nur neuere Zusammenfassungen mit Zeitstempelfilter abrufen
        logger.info(f"Retrieving summaries after timestamp: {timestamp}")
        filtered_response = requests.get(
            f"{self.api_url}/summaries?after_timestamp={timestamp}"
        )

        filtered_summaries = filtered_response.json()
        logger.info(f"Retrieved {len(filtered_summaries)} filtered summaries")

        # Es sollte mindestens eine Zusammenfassung geben
        self.assertGreaterEqual(len(filtered_summaries), 0,
                                "There should be filtered summaries")

        # Prüfen, ob unser eindeutiger Agent in den Zusammenfassungen vorkommt
        found_agent = False
        for summary in all_summaries:
            if unique_agent in summary.get("agents", []):
                found_agent = True
                logger.info(f"Found agent '{unique_agent}' in summaries")
                break

        self.assertTrue(found_agent, f"Agent '{unique_agent}' should appear in the summaries")
        logger.info("Get summaries test passed.")

    def test_bad_request_handling(self):
        """Testet wie die API fehlerhafte Anfragen behandelt"""
        logger.info("Testing bad request handling...")

        # Test mit fehlendem agent_id
        logger.info("Testing request with missing agent_id...")
        response = requests.post(
            f"{self.api_url}/summarize_conversation",
            json={
                "first_timestamp": self.first_timestamp,
                "last_timestamp": self.last_timestamp,
                "conversation": self.test_conversation
            }
        )
        self.assertEqual(response.status_code, 422,
                         "Request with missing agent_id should return error")

        # Test mit fehlenden Zeitstempeln
        logger.info("Testing request with missing timestamps...")
        response = requests.post(
            f"{self.api_url}/summarize_conversation",
            json={
                "agent_id": "test-bad-request",
                "conversation": self.test_conversation
            }
        )
        self.assertEqual(response.status_code, 422,
                         "Request with missing timestamps should return error")

        # Test mit fehlender Konversation
        logger.info("Testing request with missing conversation...")
        response = requests.post(
            f"{self.api_url}/summarize_conversation",
            json={
                "agent_id": "test-bad-request",
                "first_timestamp": self.first_timestamp,
                "last_timestamp": self.last_timestamp
            }
        )
        self.assertEqual(response.status_code, 422,
                         "Request with missing conversation should return error")

        # Test mit leerer Konversation
        logger.info("Testing request with empty conversation...")
        response = requests.post(
            f"{self.api_url}/summarize_conversation",
            json={
                "agent_id": "test-empty-conversation",
                "first_timestamp": self.first_timestamp,
                "last_timestamp": self.last_timestamp,
                "conversation": []
            }
        )
        self.assertEqual(response.status_code, 400,
                         "Request with empty conversation should return 400")

        logger.info("Bad request handling tests passed.")

    def test_timestamp_format(self):
        """Testet, ob die Zeitstempel korrekt in der Zusammenfassung verwendet werden"""
        logger.info("Testing timestamp format in summary...")

        # Spezifische Zeitstempel für diesen Test
        custom_first_ts = "2023-01-01T08:00:00.000000"
        custom_last_ts = "2023-01-01T09:30:00.000000"
        test_agent = f"test-timestamps-{datetime.now().timestamp()}"

        # Anfrage senden mit benutzerdefinierten Zeitstempeln
        response = requests.post(
            f"{self.api_url}/summarize_conversation",
            json={
                "agent_id": test_agent,
                "first_timestamp": custom_first_ts,
                "last_timestamp": custom_last_ts,
                "conversation": self.test_conversation
            }
        )

        self.assertEqual(response.status_code, 200, "Endpoint should return HTTP 200")

        # Warten, bis Zusammenfassung verarbeitet wurde
        time.sleep(1)

        # Dateiinhalt prüfen
        with open("agent_work_summaries.txt", "r", encoding="utf-8") as f:
            content = f.read()
            agent_sections = content.split("=== AGENT:")

            # Den entsprechenden Abschnitt für unseren Agent finden
            agent_section = None
            for section in agent_sections:
                if test_agent in section:
                    agent_section = section
                    break

            self.assertIsNotNone(agent_section, f"Section for agent {test_agent} should exist in file")

            # Prüfen, ob die spezifischen Zeitstempel enthalten sind
            self.assertIn(custom_first_ts, agent_section,
                         "Summary should contain exact first timestamp")
            self.assertIn(custom_last_ts, agent_section,
                         "Summary should contain exact last timestamp")

        logger.info("Timestamp format test passed.")


if __name__ == "__main__":
    # Aktuelle Zeit für Protokollierung
    start_time = datetime.now()
    logger.info(f"Tests started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Tests ausführen
    unittest.main(verbosity=2, exit=False)

    # Ausführungszeit berechnen und protokollieren
    end_time = datetime.now()
    logger.info(f"Tests completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duration: {end_time - start_time}")