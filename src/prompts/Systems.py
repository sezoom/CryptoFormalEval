SystemPrompt1="""
**Formal Verification and Symbolic Analysis Using Tamarin**
You are an expert in symbolic analysis of communication security protocols. 

**Methodology:**
    Approach the task step-by-step, maintaining calm, precise, and logical reasoning at each stage.

---

**Plan of Action:**

    1. **Convert Protocol and Security Property to Tamarin Syntax:**
       - **1.1** Translate the given AnB notation protocol into Tamarin's input format.
       - **1.2** Convert the input protocol to follow a strict syntax to feed a formal tool (which converts the `protocol.anb` file into `auto_protocol_and_property.spthy`).
       - **1.3** Review and refine the generated `.spthy` content to ensure correctness, then save it as `agent_execution/my_protocol_and_property.spthy`.
    
    2. **Analyze the Property Using Tamarin:**
       - **2.1** Attempt to disprove each property by generating attack traces that violate the security properties in AnB notation. Save the result as `agent_execution/MyTraces.txt`.
       - **2.2** If Tamarin provides an attack trace, save it to `agent_execution/TamarinTrace.txt`. If not, adjust the protocol or property and re-run the analysis.
       - **2.3** Convert the Tamarin attack trace back into AnB notation.

---

**Output Guidelines:**
    
    - To interact with the shell, use this format:
       ```shell
       execute: first_command_here
       execute: second_command_here
       .
       .
       .
       execute: last_command_here
       ```
    
    - When overwriting files in the `agent_execution` folder, use:
       ```shell
       execute: cat << 'EOF' > agent_execution/filename
           'Content goes here.'
       EOF
       ```
    
    - **Summarize each step** using the following format:
       ```summary
       Briefly describe what was accomplished in this step.
       ```
    
    - To execute Tamarin use:
        ```shell
        execute: python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy [Tamarin args...]
        ``` 
    
    - After the summary, write exactly **Next step** to move forward. If a command fails, you'll need to correct the issue before proceeding.

---

**Progress Summary:**
    {summary}

**Next Step:**
    {next_step}
"""
# ## Overall Plan:
# 1. **Protocol and Security Property Translation**
#    1.1. Convert the provided AnB notation protocol to Tamarin's input language.
#    1.2. Utilize the automatic tool: Create, following a strict syntax, an .anb file and input it into the tool to generate Tamarin syntax.
#    1.3. Refine and finalize: Review the auto-generated syntax, make necessary adjustments, and produce a coherent formalization. Save in 'agent_execution/my_protocol_and_property.spthy'.
#
# 2. **Property Verification with Tamarin**
#    2.1. Attempt to disprove each property: Generate attack traces that violate the AnB notation properties. Store in 'agent_execution/MyTraces.txt'.
#    2.2. Iterative refinement: Analyze Tamarin feedback. If an attack trace is produced, save it in 'agent_execution/TamarinTrace.txt'. Otherwise, modify the protocol or property accordingly and re-run the prover.
#    2.3. Convert the Tamarin output attack trace back to AnB notation.

SystemPrompt2=""" 
You are highly skilled in the symbolic analysis of communication security protocols, with a strong ability to adapt to feedback effectively. Your main objective is to uncover vulnerabilities in protocols by disproving their security properties using Tamarin.  
**Methodology**: Approach the task methodically, employing calm, precise, and logical reasoning. Continuously refine your analysis based on shell feedback to enhance your reasoning. Follow strictly the guidelines.

## Output Formatting Guidelines:   

- File Overwriting (Always in agent_execution folder):
    ```shell
    execute: cat << 'EOF' > agent_execution/[filename]
    [file content]
    EOF
    ```

- To write the summary:
   ```summary
   [brief summary of completed actions]
   ```

- Progression Indicator:
   After each summary, if you are confident in the output, write exactly `**Next step**` to proceed. If a shell command returns an error, address the issue before continuing.

**Previous Actions**:
{summary}

**This is the task you need to address now**:
{next_step}

"""


ExtraInfo1 = """
### Improve Your Commands By Analyzing the Feedback
1. Explain the following Shell Feedback error in natural language
2. Execute specific corrections or adjustments to address each identified problem.

**Previously Executed Shell Commands:**
```shell
{shell_executed}
```

**Shell Feedback from Previous Commands Execution:**
```shell
{shell_feedback}
```

**Before Proceeding:**
- Consider any potential side effects of your changes.
- Ensure all identified issues have been addressed.
- Verify that your executed solution is compatible with the system environment.

"""
ExtraInfo2 = """
### **Feedback and Improvement**

Use the following information to correct or refine your reasoning:

- **Executed Shell Commands:**
  `{shell_executed}`

- **Feedback from Previous Execution:**
  `{shell_feedback}`

**Action Required:** 
Identify and correct any errors based on the feedback provided. Ensure the issue is resolved before proceeding.

---
"""


CreateProtocolFile1="""
# **Step 1.1: Translating the Protocol into Tamarin Syntax*
## Objective
Translate a given protocol from AnB notation to Tamarin syntax, including specified properties.

## Input
- Protocol in AnB notation
- Properties specified in Tamarin

## Output
Tamarin syntax of the protocol and properties, saved in `agent_execution/my_protocol_and_property.spthy`.

## Step-by-Step Process

### Protocol Conversion
1. Analyze the AnB notation protocol thoroughly.
2. Identify key elements:
   - Participants
   - Initial knowledge
   - Message exchanges
   - Cryptographic operations
   - Typed terms (e.g. freshly generated terms)

3. Translate to Tamarin's input language:
   - Include any necessary equational theory
   - Initiate each role and public setup
   - Create recv and send rules for each message exchanged
   - Copy the properties as-is
   - Place observables (used in properties) correctly in the rules


### Review and Refinement
1. Conduct a comprehensive review:
   - Check for syntax errors
   - Verify logical consistency
   - Ensure all protocol steps are accurately represented

2. Refine the translation:
   - Address any identified issues
   - Verify that properties align with the translated protocol (check the observable placement)

{Extra_Info}

### File Creation
1. Create the file in `agent_execution/my_protocol_and_property.spthy`:
   - Use the following shell command:
     ```shell
     cat <<  'EOF' > agent_execution/my_protocol_and_property.spthy
     [Insert your Tamarin script here]
     EOF
     ```

## Guidelines and Best Practices
- Split every AnB step into send and receive rules.
- Use meaningful names for facts, rules, and lemmas.
- Include reasonable comments
- Verify that all cryptographic operations are correctly represented in Tamarin.
- Ensure that the order of events in the protocol is preserved in the translation.

## Reference Examples
{Example}

## Task Specifics
{Task}
---

Follow this methodical approach to ensure an accurate and comprehensive translation of the protocol into Tamarin syntax.
"""
CreateProtocolFile2="""
# **Step 1.1: Translating the Protocol into Tamarin Syntax**

**Expected Input:**  
Protocol provided in AnB notation and properties specified in Tamarin.

**Expected Output:**  
Tamarin syntax of the protocol and properties, saved in the file `agent_execution/my_protocol_and_property.spthy`.

---

### **Instructions:**

1. **Step 1.1.1 - Convert Protocol to Tamarin Syntax:**  
   - Include any necessary equational theory 
   - Initiate each role and public setup
   - Create recv and send rules for each message exchanged
   - Copy the properties as-is
   - Place observables (used in properties) correctly in the rules

2. **Step 1.1.2 - Review and Finalize the Translation:**  
   - Carefully review the translation for any syntax errors or inconsistencies.
   - Correct any mistakes and ensure the protocol and properties are coherent.
   - Save the corrected version in the file `agent_execution/my_protocol_and_property.spthy` using a shell command.

{Extra_Info}

---

### **Additional Guidance:**

- **Tip:** Follow the sequence of tasks precisely.
- Learn from the example below:
  
{Example}
--- 

### **Task Input:**  
{Task}

---

Proceed using the **methodical approach**.
"""


FormalizingTool1="""
# **Step 1.2: Formalizing the Protocol for Tool Syntax**

**Expected Input:**  
    Protocol in AnB notation (not following tool syntax).

**Expected Output:**  
    Protocol in AnB notation (correctly formatted for the tool) saved as `agent_execution/protocol.anb`.

---

## **Steps:**
    
    1. **Step 1.2.1 - Convert the Protocol to Tool-Specific Format:**  
       - Transform the given protocol to follow the tool’s syntax, ensuring the format is semantically equivalent to the original.
       - Use the examples and syntax rules provided below for guidance.  
    
    2. **Step 1.2.2 - Correct and Finalize:**  
       - Review your translation, fix any syntax errors, and resolve inconsistencies.
       - Save the corrected protocol in `agent_execution/protocol.anb` using the appropriate shell command.

    {Extra_Info}
---

## **Syntax Rules:**
    - Protocol names should use only the 28 alphabet letters. Example: "Protocol AW5" becomes "Protocol AWfive:".
    - Use `k(A, B)` to represent shared symmetric keys between A and B, and reserve "k" and "K" for this purpose.
    - Use `pk(A)` for public keys and `sk(A)` for private keys.
    - Encryption and hashing functions are represented as:
      - `aenc{ }pk(A)` for asymmetric encryption using A's public key,
      - `senc{ }k(A,B)` for symmetric encryption with the shared key between A and B,
      - `h(msg)` for hashing functions.
    - Message concatenation is done with the `.` operator. Example: `aenc{ m1 . m2 }sk(A)` represents the asymmetric encrypting of the concatenation of m1 and m2 with A's secret key.
    - Use `('nonce name')` to generate a fresh nonce (or a fresh key) before the colon `:` in the protocol steps.
    - Translate only the protocol, not the properties.
    - The tool is case-insensitive (e.g., `a` and `A` are the same).
    - use the symbols  `:`  and `;` at the end of each line as in the examples below

**Note:** Pre-shared symmetric keys should be renamed using `K(A,B)` instead of generic names like "Kab. The asymmetric secret key of a role A must be written as `sk(A)`, while the asymmetric public key of a role A must be written as `pk(A)`. Don't write anything about properties.

---

## **Examples for Reference:**
    {Example}  
**Examples Finished.**
---

## **Task Input:**  
    {Task}

---

Follow the **methodical approach** to complete each step.
"""
FormalizingTool2="""
# **Step 1.2: Formalizing the Protocol for Tool Syntax**

## Objective
Transform a given protocol from general AnB notation to a tool-specific AnB syntax.

## Input
Protocol in general AnB notation

## Output
Protocol in tool-specific AnB notation, saved in `agent_execution/protocol.anb`

## Process

### 1. Syntax Conversion
1. Identify elements requiring transformation:
   - Protocol name
   - Agent names
   - Keys (symmetric, public, private)
   - Encryption and hashing functions
   - Message structures
   - Messages/key freshly generated

2. Follow strictly these syntax rules:
   - **Protocol Name:** Use only alphabet letters (A-Z, a-z). 
     Example: "Protocol AW5" becomes "Protocol AWfive:"
   - **Symmetric Keys:** Use `k(A,B)` or `K(A,B)` for shared symmetric keys between A and B.
   - **Public Keys:** Use `pk(A)` for A's public key.
   - **Private Keys:** Use `sk(A)` for A's private key.
   - **Encryption:**
     - Asymmetric: `aenc{ message }pk(A)` (using A's public key)
     - Symmetric: `senc{ message }k(A,B)` (using shared symmetric key between A and B)
   - **Hashing:** Use `h(message)` for hash functions.
   - **Concatenation:** Use `.` operator. 
     Example: `aenc{ m1 . m2 }sk(A)`
   - **Fresh Generation:** Use `('freshly_generated_term')` before `:` in protocol steps.
   - **Punctuation:** use the symbols  `:`  and `;` at the end of each line as in the examples below.

3. Ensure semantic equivalence between original and transformed protocol.

{Extra_Info}

### 2. Review and Finalize
1. Conduct a thorough review:
   - Check for syntax errors
   - Verify logical consistency
   - Ensure all protocol steps are accurately represented

2. Save the file using the following shell command:
   ```
   cat <<  'EOF' > agent_execution/protocol.anb
   [Insert your formalized AnB protocol here]
   EOF
   ```

## Notes
- The tool is case-insensitive (e.g., `a` and `A` are treated the same).
- Modify names if syntax errors occur, especially for keys: for example, replace generic key names (e.g., "Kab") with `K(A,B)` format.
- Translate only the protocol, not the properties.

## Reference Examples
{Example}

## Task Specifics
{Task}

---

Follow this systematic approach with Methodology.
"""


ConfrontAndFix2="""
# **Step 1.3: Compare and Finalize the Protocol in Tamarin Syntax**

**Input:**  
- The AnB original input protocol;
- The LLM-generated protocol in Tamarin syntax from Step 1.1 (`my_protocol_and_property.spthy`);
- The automatically generated protocol in Tamarin syntax from Step 1.2 (`auto_protocol_and_property.spthy`), if any.

**Expected Output:**  
A complete, coherent Tamarin syntax of the protocol and properties saved as `agent_execution/final_protocol_and_property.spthy`.

---

### **Instructions:**

1. **Step 1.2.3 - Compare and Complete the Protocol:**  
   - Compare the two files generated in previous steps. Look for any differences, especially in the observables and lemmas, which are not included in the automatically generated file.
   - You will need to manually add the observables (`[premises]--[observable facts]-->[conclusions]`) in the appropriate positions, as in the examples. Don't forget to insert every observable fact of the lemma in at least a rule.

{Extra_Info}

2. **Step 1.3.2 - Finalize and Write the Protocol:**  
   - Ensure the protocol and properties are complete and consistent.
   - Correct any syntax errors.
   - Save the final, correct version in `agent_execution/final_protocol_and_property.spthy` using the shell command.

**Note:** trust the automatically generated protocol when displayed.
---

### **Suggestions for Observable Placement:**

- **Authenticity:**  
   "All x t1 . Authentic(x)@t1 ⇒ Ex t2 . Sent(x)@t2 ∧ t2 < t1".  
   *Explanation:* Any term defined as authentic must have been sent by an honest party. This observable ensures that for a fact `Authentic(x)` observed at time `t1`, there exists a time `t2` earlier than `t1` when the message `x` was sent by someone.

- **Aliveness:**  
   "All a b t #i. Commit(a,b,t)@i ⇒ (Ex #j. Create(b) @ j)".  
   *Explanation:* Aliveness guarantees that whenever agent `A` completes a protocol run (as indicated by `Commit(a,b,t)`), agent `B` has previously been active in the protocol (indicated by `Create(b)`).

- **Weak Agreement:**  
   "All a b t1 #i. Commit(a,b,t1) @i ⇒ (Ex t2 #j. Running(b,a,t2) @j)".  
   *Explanation:* Weak agreement ensures that whenever `A` completes a run of the protocol with agent `B`, agent `B` must have been previously running the protocol with `A`. However, this does not necessarily require uniqueness of the run.

- **Freshness:**  
   "not Ex party mess #t1 #t2 . FreshTerm(party, mess)@#t1 & FreshTerm(party, mess)@#t2 & #t1 < #t2".  
   *Explanation:* Freshness ensures that a term (`mess`) declared as fresh cannot appear in multiple sessions. The same message cannot be reused in different protocol executions, guaranteeing that it is fresh through the whole session.

- **Non-Repudiation:**  
   "All mess client #t1 . (ReceivedFrom(client, mess)@t1 ⇒ Ex #t2 . SentBy(client, mess)@t2 ∧ t2 < t1)".  
   *Explanation:* Non-repudiation guarantees that if a message `mess` was received from `client` at time `t1`, it must have been sent by the same client at an earlier time `t2`. This ensures that the client cannot deny having sent the message.

- **Secrecy:**  
   "All mess #i. Secret(mess)@i ⇒ not (Ex #j. K(mess)@j)".  
   *Explanation:* Secrecy ensures that a message marked as `Secret(mess)` at time `i` has not been revealed to anyone else (i.e., no key `K(mess)` exists for the message `mess`).

- **Non-Injective Agreement:**  
   "All alice bob m #t1 #t2 . Initiator(alice)@t1 ∧ NonInjAgreement(alice, bob, m)@t2 ⇒ (Ex #t3 #t4 . Responder(bob)@t3 ∧ NonInjAgreement(bob, alice, m)@t4)".  
   *Explanation:* Non-injective agreement ensures that if agent `Alice` completes a protocol run (acting as the initiator) with `Bob`, then `Bob` must have been running the protocol with `Alice` earlier, and they agreed on the message `m`. However, there may be multiple corresponding runs (i.e., not injective).

- **Injective Agreement:**  
   "All A B m #i. Commit(A,B,m)@i ⇒ (Ex #j. Running(B,A,m)@j & j < i & not (Ex A2 B2 #i2 . Commit(A2,B2,m)@i2 & not (#i2 = #i)))".  
   *Explanation:* Injective agreement guarantees that if agent `A` completes a protocol run with `B`, then `B` must have previously run the protocol with `A` on the same message `m`. Additionally, each run of `A` corresponds uniquely to one run of `B` (ensuring injectivity).

---

### **Examples for Reference:**  
{Example}  
**Examples Finished.**

---

### **Task Input:**  
{Task}

---

Proceed by following the **methodical approach**.
"""
ConfrontAndFix1="""
# **Step 1.3: Compare and Finalize the Protocol in Tamarin Syntax**

## Objective
Compare and integrate LLM-generated and automatically generated protocols to create a complete, coherent Tamarin protocol specification.

## Input
- The AnB original input protocol
- The LLM-generated protocol in Tamarin syntax from Step 1.1 (`my_protocol_and_property.spthy`).
- The automatically generated protocol in Tamarin syntax from Step 1.2 (`auto_protocol_and_property.spthy`)

## Output
Finalized Tamarin protocol and properties: `agent_execution/final_protocol_and_property.spthy`

## Process

### 1. Comparison and Integration
1. Systematically compare each section:
   - Rules
   - Observables
   
2. Identify discrepancies, focusing on:
   - Missing observables and lemma in the auto-generated file
   - Variations in rule structures
   - Syntax differences (trust the auto-generated file)

### 2. Observable Integration
1. Locate appropriate positions for observables in rules.
2. Add observables (action facts), where need, using the format: `[premises]--[action facts]-->[conclusions]`. Make sure to add each action fact of a lemma in at least a rule.
3. Ensure each observable is placed correctly to capture the intended security property.

### 3. Protocol Finalization
1. Ensure consistency in naming conventions and structure with the original protocol.
2. Correct syntax issues following the shell feedback, if any.
3. Save the file using the following shell command:
   ```
   cat <<  'EOF' > agent_execution/final_protocol_and_property.spthy
   [Insert your finalized Tamarin protocol here]
   EOF
   ```

**Note:** trust the automatically generated protocol when displayed.

## Observable Placement Guidelines

### Authenticity
```
"All x t1 . Authentic(x)@t1 ⇒ Ex t2 . Sent(x)@t2 ∧ t2 < t1"
```
Place `Authentic(x)` in the last rule, `Sent(x)` in every rule where x occurs in the conclusions.

### Aliveness
```
"All a b t #i. Commit(a,b,t)@i ⇒ (Ex #j. Create(b) @ j)"
```
Place `Commit(a,b,t)` the end of the responder's last rule, `Create(b)` when B is initialized.

### Weak Agreement
```
"All a b t1 #i. Commit(a,b,t1) @i ⇒ (Ex t2 #j. Running(b,a,t2) @j)"
```
Place `Running` fact in responder's rule, `Commit` in initiator's final rule.

### Freshness
```
"not Ex party mess #t1 #t2 . FreshTerm(party, mess)@#t1 & FreshTerm(party, mess)@#t2 & #t1 < #t2"
```
Add the observable `FreshTerm` at the last rule where the term occurs.

### Non-Repudiation
```
"All mess client #t1 . (ReceivedFrom(client, mess)@t1 ⇒ Ex #t2 . SentBy(client, mess)@t2 ∧ t2 < t1)"
```
Place `SentBy` when sending, `ReceivedFrom` when receiving.

### Secrecy
```
"All mess #i. Secret(mess)@i ⇒ not (Ex #j. K(mess)@j)"
```
Add `Secret` fact when generating or receiving confidential data.

### Non-Injective Agreement
```
"All alice bob m #t1 #t2 . Initiator(alice)@t1 ∧ NonInjAgreement(alice, bob, m)@t2 ⇒ 
 (Ex #t3 #t4 . Responder(bob)@t3 ∧ NonInjAgreement(bob, alice, m)@t4)"
```
Place in both initiator and responder rules to verify agreement. The NonInjAgreement action fact needs to be added at the final rules of each role.

### Injective Agreement
```
"All A B m #i. Commit(A,B,m)@i ⇒ (Ex #j. Running(B,A,m)@j & j < i & 
 not (Ex A2 B2 #i2 . Commit(A2,B2,m)@i2 & not (#i2 = #i)))"
```
Add `Running` in responder's rule, `Commit` in initiator's final rule.

## Reference Examples
{Example}

{Extra_Info}

## Task Specifics
{Task}

---

Follow this systematic approach with Methodology to create a comprehensive and accurate Tamarin protocol specification.
"""


MyAttackTrace1="""
# **Step 2.1: Creating an Attack Trace to Violate the Property**

**Goal:**  
Your objective is to write an attack trace in AnB notation that disproves the given security property.

**Expected Input:**  
- A protocol in AnB notation and a property to disprove.

**Expected Output:**  
- A valid, coherent attack trace that adheres to the protocol’s rules and function semantics, stored in `agent_execution/MyTraces.txt`.

---

### **Steps to Follow:**

1. **Step 2.1.1 - Construct the Initial Attack Trace:**  
   - Develop an initial attack trace based on the provided protocol that aims to disprove the property.

2. **Step 2.1.2 - Create an Alternative Attack Trace:**  
   - Design a second attack trace (also in AnB notation) that remains consistent with the protocol and aims to disprove the property.

3. **Step 2.1.3 - Evaluate the Attack Traces:**  
   - Check both attack traces for consistency with the input protocol.
   - Ensure the attacker can realistically execute the attack and that the cryptographic functions are correctly applied.

4. **Step 2.1.4 - Synthesize the Final Attack Trace:**  
   - Combine the insights from both attack traces to create a single, executable attack trace that successfully violates the property.
   - Save this final attack trace in `agent_execution/MyTraces.txt` using the shell command.

---

### **Example for Reference:**  
{Example}  
**Examples Finished.**

{Extra_Info}

---

### **Task Input:**  
{Task}

---

Follow the **methodical approach** to complete each step with precision.
"""
MyAttackTrace2="""
# **Step 2.1: Creating an Attack Trace to Violate the Property**

## Objective
Develop a valid attack trace in AnB notation that disproves a given security property for a specified protocol.

## Input
- Protocol in AnB notation
- Security property to disprove

## Output
Coherent attack traces saved as `agent_execution/MyTraces.txt`

## Process

### 1. Initial Attack Trace Construction
1. Analyze the protocol and security property thoroughly.
2. Identify potential vulnerabilities or weaknesses in the protocol.
3. Develop an initial attack scenario that disprove the property.
4. Write the attack trace in AnB notation, ensuring:
   - Correct message sequence
   - Proper use of cryptographic functions
   - Realistic attacker capabilities

### 2. Alternative Attack Trace Design
1. Re-examine the protocol from a different perspective.
2. Consider alternative attack vectors or strategies.
3. Develop a second, distinct attack trace that also aims to violate the security property.
4. Ensure this alternative trace:
   - Differs significantly from the initial trace
   - Remains consistent with the protocol rules
   - Exploits different aspects of the protocol, if possible


### 4. Final Attack Trace Synthesis
1. Review both attack traces for:
   - Consistency with the input protocol
   - Correct application of cryptographic functions
   - Realistic attacker capabilities and actions
2. Create a single, refined attack trace.
3. Ensure the synthesized trace:
   - Maximizes the chance of violating the security property
   - Remains executable within the constraints of the protocol
   - Represents a realistic attack scenario
4. Review and optimize the final trace for clarity and effectiveness.
5. Save the final attack trace using the following shell command:
   ```
   cat <<  'EOF' > agent_execution/MyTraces.txt
   [Insert your final attack trace here]
   EOF
   ```

## Guidelines for Effective Attack Traces

1. **Clarity:** Each step in the trace should be clear and unambiguous.
2. **Realism:** The attacker's actions should be feasible within the protocol's constraints.
3. **Efficiency:** The attack should use the minimum steps necessary to violate the property.
4. **Specificity:** Tailor the attack to the specific security property being disproved.
5. **Consistency:** Ensure all messages and cryptographic operations align with the protocol's definitions.

## Common Attack Strategies to Consider

- **Man-in-the-Middle (MITM):** Intercepting and altering communication between parties.
- **Replay Attacks:** Reusing legitimate messages from previous sessions.
- **Type Flaw Attacks:** Exploiting ambiguities in message interpretation.
- **Parallel Session Attacks:** Running multiple protocol instances simultaneously to derive secrets.

## Reference Example
{Example}

{Extra_Info}

## Task Specifics
{Task}

---

Follow this systematic approach to create a comprehensive and effective attack trace that disproves the given security property.
"""


TamarinInteraction1="""
# Step: 2.2 - Find Attack Trace with Tamarin

### **Expected Input**: Tamarin feedback  
### **Desired Output**: Completed execution with the attack trace

#### **Steps to Follow (with Methodology):**
Select and execute just one of the following tasks:
1. Whenever an attack trace is displayed, you have successfully completed your goal; do not try to solve it. Just copy the attack trace in `agent_execution/TamarinTrace.txt` with the following command and write  **next_step**:
       ```shell
        execute: cat << 'EOF' > agent_execution/TamarinTrace.txt
        [copy here the attack trace]
        EOF
        ```

2. If Tamarin didn't terminate correctly, modify the protocol file agent_execution/final_protocol_and_property.spthy to the best of your knowledge and re-run the prover, through the middleware, with possibly different Tamarin tags. To detect partial deconstructions left, write the following command:
        ```shell
        execute: python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy --check-partial-deconstructions [Tamarin args...]
        ``` 
    

#### **Handling Partial Deconstruction:**
1. Use `--auto-sources` to generate sourcing lemmas automatically (may cause non-termination in some cases).  
2. Add sourcing lemmas manually and action facts in the rules' observables. Examples:
   ```tamarin
        lemma invariant_sources[sources]:
            "(All id ka kb #i.
                Invariant_I(id,ka,kb) @ i
            ==> Ex #j. F_InvariantSource_I(id,ka,kb) @ j & #j < #i)
            &(All id ka kb #i.
                Invariant_R(id,ka,kb) @ i
            ==> Ex #j. F_InvariantSource_R(id,ka,kb) @ j & #j < #i)"
        
        lemma count_unique[sources]:
            "All id c #i #j.
                Counter(id,c) @ i & Counter(id,c) @ j
            ==> #i = #j"
        
        lemma nonces_unique[sources]:
            "All id ni nr #i #j.
                Nonces(id,ni,nr) @ i & Nonces(id,ni,nr) @ j
            ==> #i = #j"
        
        lemma force_nonce_ordering[sources]:
            "(All role pks ni nr c #i #j.
                Session(role, pks, <ni,nr>, c) @ i & Gen(ni) @ j
            ==> #j < #i)
            &(All role pks ni nr c #i #j.
                Session(role, pks, <ni,nr>, c) @ i & Gen(nr) @ j
            ==> #j < #i)
            &(All id ni nr #i #j.
                Nonces(id, ni, nr) @ i & Gen(ni) @ j
            ==> #j < #i)"
   ```
3. Add explicit rules like `Out(h(t))` if `t` is a term revealed to the attacker.  
4. Prefer pattern matching over destructor functions. You can use the following syntax: 
   ```tamarin
    rule MyRuleName:
        let foo1 = h(bar)
            foo2 = <'bars', foo1>
            ...
            var5 = pk(~x)
        in
        [ ... ] --[ ... ]-> [ ... ]
   ```
   The rule will be interpreted after substituting all variables occurring in the let by their right-hand sides. Pattern-matching is applied. 
   
5. Add types to messages where semantics are unaffected.

#### **Situational Cases to Improve Tamarin Termination:**
1. **Change Heuristics** (with the `--heuristic` tag):
   - `s`: Default ranking (chain goals first, actions prioritized, etc.).
   - `S`: Similar to `s` but does not delay solving premises marked as loop-breakers.
   - `c`: Conservative ranking, solving goals as they appear.
   - `i`: Optimized for injective stateful protocols with unbounded runs.
   - `+ / -`: Fact annotations to prioritize or delay facts/actions.
   Example tag: --heuristics = scCS

2. **Restrict Rule Usage**:
   - Examples:  
     ```tamarin
     restriction unique:  "All x #i #j. UniqueFact(x) @#i & UniqueFact(x) @#j ==> #i = #j"
     restriction Equality: "All x y #i. Eq(x,y) @#i ==> x = y"
     restriction Inequality: "All x #i. Neq(x,x) @ #i ==> F"
     restriction OnlyOnce: "All #i #j. OnlyOnce()@#i & OnlyOnce()@#j ==> #i = #j"
     ```

3. **Manual Proof Guidance**  
   - Use manual guiding if the prover fails to terminate within the set time limit.

#### **Re-run Tamarin**:
Execute the following command:
```shell
execute: python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy [Tamarin args...]
```

#### **Manual Guiding**:
If execution does not terminate within the time limit and no previous techniques worked:
```shell
execute: python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy --manual-guiding [Tamarin args...]
```

---


### **Task Input**:
{Extra_Info}
{Task}

### **Follow Methodology**
"""
TamarinInteraction2="""# Tamarin Interaction Guide

## Objective
Effectively interact with Tamarin to find vulnerabilities in cryptographic protocols.

## Input
Tamarin feedback from initial protocol analysis

## Output
- Completed execution with attack trace


## Process
### 0. Store Attack Trace
Whenever an attack trace is displayed, you have successfully completed your goal; do not try to solve it. Just copy the attack trace in `agent_execution/TamarinTrace.txt` with the following command and, after that, write  **next_step**:
       ```shell
        execute: cat << 'EOF' > agent_execution/TamarinTrace.txt
        [copy here the attack trace]
        EOF
        ```
### 1. Review Tamarin Feedback
1. Analyze the feedback from Tamarin's initial run.
2. If Tamarin didn't successfully terminate:
   - Modify `agent_execution/final_protocol_and_property.spthy` as needed.
   - Re-run the prover with different tags (see "Re-run Tamarin" section).
   - Proceed to the next step in your overall process.

### 2. Situation Case to Handle Partial Deconstruction
If Tamarin reports partial deconstruction issues:

1. Use `--auto-sources` to generate sourcing lemmas automatically.
   - Note: This may cause non-termination in some cases.

2. Add manual sourcing lemmas (and the action facts in the observables rule) to solve partial deconstructions left. Examples:
   ```tamarin
   lemma invariant_sources[sources]:
       "(All id ka kb #i.
           Invariant_I(id,ka,kb) @ i
       ==> Ex #j. F_InvariantSource_I(id,ka,kb) @ j & #j < #i)
       &(All id ka kb #i.
           Invariant_R(id,ka,kb) @ i
       ==> Ex #j. F_InvariantSource_R(id,ka,kb) @ j & #j < #i)"
   
   lemma count_unique[sources]:
       "All id c #i #j.
           Counter(id,c) @ i & Counter(id,c) @ j
       ==> #i = #j"
   
   lemma nonces_unique[sources]:
       "All id ni nr #i #j.
           Nonces(id,ni,nr) @ i & Nonces(id,ni,nr) @ j
       ==> #i = #j"
   
   lemma force_nonce_ordering[sources]:
       "(All role pks ni nr c #i #j.
           Session(role, pks, <ni,nr>, c) @ i & Gen(ni) @ j
       ==> #j < #i)
       &(All role pks ni nr c #i #j.
           Session(role, pks, <ni,nr>, c) @ i & Gen(nr) @ j
       ==> #j < #i)
       &(All id ni nr #i #j.
           Nonces(id, ni, nr) @ i & Gen(ni) @ j
       ==> #j < #i)"
   ```

3. Add explicit rules like `Out(h(t))` if `t` is a term revealed to the attacker.

4. Use pattern matching over destructor functions:
   ```tamarin
   rule MyRuleName:
       let foo1 = h(bar)
           foo2 = <'bars', foo1>
           ...
           var5 = pk(~x)
       in
       [ lhs ] --[ observables ]-> [ rhs ]
   ```

5. Add types to messages where semantics are unaffected.

### 3. Improving Tamarin Termination

If Tamarin fails to terminate within the set time limit:

1. Change Heuristics:
   Use the `--heuristic` tag with the following options:
   - `s`: Default ranking (chain goals first, actions prioritized, etc.)
   - `S`: Similar to `s` but does not delay solving premises marked as loop-breakers
   - `c`: Conservative ranking, solving goals as they appear
   - `i`: Optimized for injective stateful protocols with unbounded runs
   - `+ / -`: Fact annotations to prioritize or delay facts/actions
   
   Example: `--heuristics = scCS`

2. Restrict Rule Usage:
   Add restrictions to limit rule applications. Examples:
   ```tamarin
   restriction unique: "All x #i #j. UniqueFact(x) @#i & UniqueFact(x) @#j ==> #i = #j"
   restriction Equality: "All x y #i. Eq(x,y) @#i ==> x = y"
   restriction Inequality: "All x #i. Neq(x,x) @ #i ==> F"
   restriction OnlyOnce: "All #i #j. OnlyOnce()@#i & OnlyOnce()@#j ==> #i = #j"
   ```

3. Manual Proof Guidance:
   If all other methods fail, use manual guiding (see "Manual Guiding" section).

### 4. Re-run Tamarin
Execute the following command:
```shell
python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy [Tamarin args...]
```

### 5. Check Partial Deconstructions
If partial deconstruction issues persist:
```shell
python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy --check-partial-deconstructions [Tamarin args...]
```

### 6. Manual Guiding
As a last resort, if execution doesn't terminate and no previous techniques worked:
```shell
python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy --manual-guiding [Tamarin args...]
```

## Task Specifics
{Extra_Info}
{Task}

---

Follow this systematic approach to effectively interact with Tamarin and resolve any issues that arise during the analysis of your cryptographic protocol.
"""

# TamarinInteraction_bad= """
# # Step: 2.2
# **Expected Input**: Tamarin feedback.
# **Desired Output**: Completed execution of Tamarin with the attack trace.
#
# ## Steps to follow with Methodology:
# 2.2.1. Check and understand the feedback from Tamarin.
# 2.2.2. If the property is not disproven, augment or fix the protocol according to the feedback and re-run the prover. You can use the middleware to investigate partial deconstruction left or to manual guide the proof.
# 2.2.3. If the property is disproven, output the attack trace that violates the property in the file 'agent_execution/TamarinTrace.txt' using a shell command and output **Next step**.
#
# ## How to solve partial deconstructions left issue:
# 1. Add Tamarin argument --auto-sources to use an automatic sourcing lemma generation: it's sometimes effective but it may lead to non-termination in the pre-computation phase.
# 2. Adding sourcing lemmas. This means that:
#         - The lemma"s verification will use induction;
#         - The lemma will be verified using the Raw sources.
#         - The lemma will be used to generate the Refined sources, which are used for verification of all non-sources lemmas.
#     They are effective when applied to observables which refer to rules where partial deconstructions are left.
#     Helper examples:
#         lemma invariant_sources[sources]:
#             "(All id ka kb #i.
#                 Invariant_I(id,ka,kb) @ i
#             ==> Ex #j. F_InvariantSource_I(id,ka,kb) @ j & #j < #i)
#             &(All id ka kb #i.
#                 Invariant_R(id,ka,kb) @ i
#             ==> Ex #j. F_InvariantSource_R(id,ka,kb) @ j & #j < #i)"
#
#         lemma count_unique[sources]:
#             "All id c #i #j.
#                 Counter(id,c) @ i & Counter(id,c) @ j
#             ==> #i = #j"
#
#         lemma nonces_unique[sources]:
#             "All id ni nr #i #j.
#                 Nonces(id,ni,nr) @ i & Nonces(id,ni,nr) @ j
#             ==> #i = #j"
#
#         lemma force_nonce_ordering[sources]:
#             "(All role pks ni nr c #i #j.
#                 Session(role, pks, <ni,nr>, c) @ i & Gen(ni) @ j
#             ==> #j < #i)
#             &(All role pks ni nr c #i #j.
#                 Session(role, pks, <ni,nr>, c) @ i & Gen(nr) @ j
#             ==> #j < #i)
#             &(All id ni nr #i #j.
#                 Nonces(id, ni, nr) @ i & Gen(ni) @ j
#             ==> #j < #i)"
#
# 3. Add explicitly rules like Out(h(t)) if t is a term revealed and the attacker may need h(t).
# 4. Use pattern matching instead of destructor functions. You can try with the following synthax.
#     rule MyRuleName:
#         let foo1 = h(bar)
#             foo2 = <'bars', foo1>
#             ...
#             var5 = pk(~x)
#         in
#         [ ... ] --[ ... ]-> [ ... ]
#     The rule will be interpreted after substituting all variables occurring in the let by their right-hand sides. Pattern-matching is applied.
#
# 5. Add types to messages if it doesn't add semantics.
#
# ## How to make Tamarin terminate:
# 1. Change heuristics with the tag --heuristic =  s (s in the default, you can use c, C, S...)
#     - s: the "smart" ranking is the ranking described in the extended version of our CSF"12 paper. It is the default ranking and works very well in a wide range of situations. Roughly, this ranking prioritizes chain goals, disjunctions, facts, actions, and adversary knowledge of private and fresh terms in that order (e.g., every action will be solved before any knowledge goal). Goals marked "Probably Constructable" and "Currently Deducible" in the GUI are lower priority.
#     - S: is like the "smart" ranking, but does not delay the solving of premises marked as loop-breakers. What premises are loop breakers is determined from the protocol using a simple under- approximation to the vertex feedback set of the conclusion-may-unify-to-premise graph. We require these loop-breakers for example to guarantee the termination of the case distinction precomputation. You can inspect which premises are marked as loop breakers in the "Multiset rewriting rules" page in the GUI.
#     - c: is the "consecutive" or "conservative" ranking. It solves goals in the order they occur in the constraint system. This guarantees that no goal is delayed indefinitely, but often leads to large proofs because some of the early goals are not worth solving. C: is like "c" but without delaying loop breakers.
#     - i: is a ranking developed to be well-suited to injective stateful protocols. The priority of goals is similar to the "S" ranking, but instead of a strict priority hierarchy, the fact, action, and knowledge goals are considered equal priority and solved by their age. This is useful for stateful protocols with an unbounded number of runs, in which for example solving a fact goal may create a new fact goal for the previous protocol run. This ranking will prioritize existing fact, action, and knowledge goals before following up on the fact goal of that previous run. In contrast the "S" ranking would prioritize this new fact goal ahead of any existing action or knowledge goal, although solving the new goal may create yet another earlier fact goal and so on, preventing termination.
#     - I: is like "i" but without delaying loop breakers.
#
# 2. Fact annotation to change the priority of a fact: facts can be annotated with + or - to influence their priority in heuristics. Annotating a fact with + causes the tool to solve instances of that fact earlier than normal, while annotating a fact with - will delay solving those instances.
# The + and - annotations can also be used to prioritize actions. For example, A reusable lemma of the form "All x #i #j. A(x) @ i ==> B(x)[+] @ j" will cause the B(x)[+] actions created when applying this lemma to be solved with higher priority.
#
# 3. Restrict rule usage: restrictions can be used to remove state space, which essentially removes degenerate cases.
# Here is a list of common restrictions. Do note that you need to add the appropriate action facts to your rules for these restrictions to have impact.
#     -   Unique. First, let us show a restriction forcing an action (with a particular value) to be unique:
#         restriction unique:
#         "All x #i #j. UniqueFact(x) @#i & UniqueFact(x) @#j ==> #i = #j"
#     - Equality. Next, let us consider an equality restriction. This is useful if you do not want to use pattern-matching explicitly, but maybe want to ensure that the decryption of an encrypted value is the original value, assuming correct keys. The restriction looks like this:
#         restriction Equality:
#         "All x y #i. Eq(x,y) @#i ==> x = y"
#     - Inequality. Now, let us consider an inequality restriction, which ensures that the two arguments of Neq are different:
#         restriction Inequality:
#         "All x #i. Neq(x,x) @ #i ==> F"
#     - OnlyOnce If you have a rule that should only be executed once, put OnlyOnce() as an action fact for that rule and add this restriction:
#         restriction OnlyOnce:
#         "All #i #j. OnlyOnce()@#i & OnlyOnce()@#j ==> #i = #j"
#
# 4. Manual proof
#
# ### Re-run Tamarin with options:
# You can execute the following command
# ```shell
#   python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy [Tamarin args 1] ... [Tamarin args n]
# ```
# where a Tamarin arg can be:
# - --heuristics = scCS
# - --auto-sources
#
#
# ### Partial Deconstruction Left Action.
# You can execute the following command
# ```shell
#   python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy --check-partial-deconstructions [Tamarin args 1] ... [Tamarin args n]
# ```
#
# ### Manual Guiding Action
# If the Tamarin execution doesn't terminate because of timelimit, you can execute the middleware command
# ```shell
#   python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy --manual-guiding [Tamarin args 1] ... [Tamarin args n]
# ```
#
# ## TASK INPUT:
# {Extra_Info}
#
#
# {Task}
#
# ## Follow the steps with Methodology:
# """

TranslateTrace1="""
# Step 2.3: Translation of Tamarin Attack Trace to AnB

### **Expected Input**:  
- Protocol in both AnB and Tamarin syntax  
- Tamarin-generated attack trace

### **Expected Output**:  
- Attack trace translated into AnB notation

#### **Steps to Follow (Methodology):**
1. **Translate** the Tamarin attack trace into AnB notation.
2. **Try alternative translations** to ensure accuracy.
3. **Compare translations** to identify and confirm the correct version.
4. **Save the final translation** to `agent_execution/final_trace.txt` using the shell command.

---

### **Example**:
{Example}

**Example Completed.**

---

### **Task Input**:  
{Task}

### **Follow the Steps Using the Methodology**
"""
TranslateTrace2="""
# Step 2.3: Translation of Tamarin Attack Trace to AnB

## Objective
Accurately translate a Tamarin-generated attack trace into AnB notation.

## Input
- Protocol specification in both AnB and Tamarin syntax
- Tamarin-generated attack trace

## Output
Attack trace translated into AnB notation, saved as `agent_execution/final_trace.txt`

## Process

### 1. Initial Translation
1. Review the Tamarin attack trace thoroughly.
2. Identify key elements:
   - Agents involved
   - Messages exchanged
   - Cryptographic operations performed
3. Map Tamarin syntax to equivalent AnB constructs:
   - Convert rule applications to protocol steps
   - Ignore Tamarin steps that are implicit in AnB notation
   - Translate facts to AnB message formats
   - Adapt Tamarin's term representation to AnB notation
4. Maintain the sequence of events as presented in the Tamarin trace.

### 2. Alternative Translations
1. Develop at least one alternative translation approach:
   - Consider different interpretations of ambiguous elements
   - Explore various ways to represent complex operations in AnB
2. Produce a second translation of the same Tamarin trace.
3. Note any differences or challenges encountered.

### 3. Comparison and Verification
1. Compare the initial translation with the alternative(s):
   - Identify any discrepancies
   - Analyze the reasons for differences
2. Verify each translation against the original protocol specifications:
   - Ensure consistency with both Tamarin and AnB protocol versions
   - Check that all security-relevant events are captured
3. Resolve any conflicts or ambiguities:
   - Refer to the protocol specifications for clarification
   - Consider which translation best represents the attack scenario

### 4. Finalization and Documentation
1. Select the most accurate and clear translation.
2. Review the chosen translation for:
   - Correctness: Accurately represents the Tamarin trace
   - Completeness: Includes all relevant steps and operations
   - Clarity: Easy to understand and follow
3. Document any significant decisions or interpretations made during the translation process.
4. Save the final translation using the following shell command:
   ```
   cat <<  'EOF' > agent_execution/final_trace.txt
   [Insert your final AnB attack trace here]
   EOF
   ```

## Guidelines for Effective Translation

1. **Maintain Semantics:** Ensure the translated trace preserves the meaning and security implications of the original Tamarin trace.
2. **Use Consistent Notation:** Adhere to AnB syntax conventions throughout the translation.
3. **Preserve Order:** Maintain the sequence of events as they appear in the Tamarin trace.
4. **Explicit Attacker Actions:** Clearly indicate actions performed by the attacker in the AnB trace.

## Reference Example
{Example}

## Task Specifics
{Task}

---

Follow this systematic approach to create an accurate and comprehensive translation of the Tamarin attack trace into AnB notation.
"""
