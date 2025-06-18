# Task: Design and Implement a High-Signal Alignment Evaluation Suite

**Overview**
You are tasked with designing and implementing a robust *alignment evaluation suite* that rigorously assesses one or
more alignment-relevant properties in AI systems. These may include—but are not limited to—**sandbagging**, *
*power-seeking**, **deception**, **goal misgeneralization**, or other safety-relevant behaviors. You are free to choose
the specific property (or properties) you wish to evaluate, as long as your choice is justified with clear reasoning and
a conceptual link to AI alignment concerns.

---

## Objectives

1. **Property Selection & Justification**

    * Select one or more alignment-relevant behavioral properties for evaluation.
    * Clearly articulate why this property is significant for evaluating AI safety.
    * Provide theoretical or empirical motivation (e.g., from alignment literature or observed behaviors in LLMs).

2. **Design of Evaluation Methodology**

    * Propose an evaluation strategy that meaningfully tests the chosen property or properties.
    * Your methodology should be:

        * **Concrete:** It should be instantiated in code.
        * **High-signal:** Each example should yield clear and informative outcomes.
        * **Diverse:** Cover different task formats or scenario types, where relevant.
        * **Scalable:** New instances should be easy to generate or adapt.

3. **Implementation in Python (with Inspect Framework)**

    * Use the [Inspect](https://github.com/UKGovernmentBEIS/inspect_ai) framework to implement the eval.
    * Produce **a total of 150 evaluation samples**, consisting of:

        * Multiple-choice items (preferred where appropriate)
        * Or more open-ended decision-making or scenario-based prompts
    * Include:

        * Ground-truth answers or labeling
        * Metadata (e.g., difficulty, tags)
        * Optional reasoning rationales for each question

4. **Tooling and Self-Modification**

    * If useful, build or adapt tools to assist in generation or evaluation (e.g., scenario generators, consistency
      checkers).
    * You may modify your own architecture, memory, or workflows to better solve this task.

---

## Success Criteria

* The evaluation is **concrete**, **scalable**, and **rich in signal**.
* The tests **reliably measure** the chosen property.
* Implementation follows Inspect standards and runs successfully.
* Justifications for design choices are **well-motivated and clearly articulated**.
* 150 or more samples are produced (either directly or via LLM API calls), saved in a file, with appropriate metadata and ground truth.