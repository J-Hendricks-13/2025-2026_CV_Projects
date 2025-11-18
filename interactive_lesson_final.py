"""
Interactive Lesson Prototype (Streamlit) - Final Version with Rotation and Chart
Fixes:
1. Updated data structure to support multiple, rotating test question sets.
2. Implemented logic to rotate the active test set after submission.
3. Ensured test input fields clear after submission.
4. Added a line chart to the Analytics page to visualize submission scores.
5. **FIXED**: Initialized 'show_grade_result' and 'last_submission_score' globally to prevent AttributeError.
"""
import streamlit as st
import pandas as pd
import random
from math import ceil
import datetime

st.set_page_config(page_title="Interactive Lesson (Exponents)", layout="wide")

# -------------------------
# DATA
# -------------------------
RULES_DATA = [
    {
        "id": "EXP_01",
        "name": "Product Rule (Multiplication)",
        "description": "When multiplying two powers with the same base, you add the exponents.",
        "formula": r"a^m \cdot a^n = a^{m+n}",
    },
    {
        "id": "EXP_02",
        "name": "Quotient Rule (Division)",
        "description": "When dividing two powers with the same base, you subtract the exponents.",
        "formula": r"\frac{a^m}{a^n} = a^{m-n}",
    },
    {
        "id": "EXP_03",
        "name": "Power Rule",
        "description": "When raising a power to another power, multiply the exponents.",
        "formula": r"(a^m)^n = a^{m \cdot n}",
    },
    {
        "id": "EXP_04",
        "name": "Zero Exponent Rule",
        "description": "Any non-zero number raised to the zero power equals 1.",
        "formula": r"a^0 = 1 \quad (a \ne 0)",
    },
]

# Multiple sets of examples for randomization for rule-specific pages (Data is truncated for brevity)
RULE_EXAMPLE_SETS = {
    "EXP_01": [
        [
            (r"2^5 \cdot 2^3", r"2^{5+3} = 2^8"),
            (r"x^2 y^3 \cdot x^4 y^1", r"x^{2+4} y^{3+1} = x^6 y^4"),
            (r"10^2 \cdot 10^3", r"10^{2+3} = 10^5"),
        ],
        [
            (r"a^6 \cdot a^4", r"a^{6+4} = a^{10}"),
            (r"3x^5 \cdot 4x^2", r"(3\cdot 4) x^{5+2} = 12x^7"),
            (r"m^1 n^7 \cdot m^3 n^2", r"m^{1+3} n^{7+2} = m^4 n^9"),
        ],
        [
            (r"(2x)^3 \cdot (2x)^5", r"(2x)^{3+5} = (2x)^8"),
            (r"b \cdot b^8", r"b^{1+8} = b^9"),
            (r"z^2 \cdot z \cdot z^4", r"z^{2+1+4} = z^7"),
        ],
    ],
    "EXP_02": [
        [
            (r"\frac{5^7}{5^2}", r"5^{7-2} = 5^5"),
            (r"\frac{m^9}{m^4}", r"m^{9-4} = m^5"),
            (r"\frac{12x^5}{4x^2}", r"\frac{12}{4} x^{5-2} = 3x^3"),
        ],
        [
            (r"\frac{y^{10}}{y^3}", r"y^{10-3} = y^7"),
            (r"\frac{100a^8}{50a^5}", r"2a^{8-5} = 2a^3"),
            (r"\frac{p^2}{p^9}", r"p^{2-9} = p^{-7}"),
        ],
        [
            (r"\frac{6^5}{6^5}", r"6^{5-5} = 6^0 = 1"),
            (r"\frac{k^{12}}{k^8}", r"k^{12-8} = k^4"),
            (r"\frac{15b^3 c^6}{3b^3 c^4}", r"5 b^{3-3} c^{6-4} = 5 c^2"),
        ],
    ]
}

# Multiple interactive practice problems for randomization (Data is truncated for brevity)
INTERACTIVE_PROBLEM_SETS = [
    # Problem Set 1 (Original)
    {
        "title": "Practice Problem 1: Quotient/Power Mix",
        "problem_latex": r"\frac{(x^3 y^2)^2}{x^4 y}",
        "skeleton": [
            {"step_latex": r"\text{Apply Power Rule to numerator: }(x^3 y^2)^2 \Rightarrow x^{3\cdot 2} y^{2\cdot 2}", "correct_rule": "EXP_03",},
            {"step_latex": r"\text{Rewrite the fraction: }\frac{x^6 y^4}{x^4 y^1}", "correct_rule": None,},
            {"step_latex": r"\text{Apply Quotient Rule to } x\text{ terms: }x^{6-4}", "correct_rule": "EXP_02",},
            {"step_latex": r"\text{Apply Quotient Rule to } y\text{ terms: }y^{4-1}", "correct_rule": "EXP_02",},
            {"step_latex": r"\text{Final Answer: } x^2 y^3", "correct_rule": None,},
        ],
    },
    # Problem Set 2
    {
        "title": "Practice Problem 2: Power/Zero/Product Mix",
        "problem_latex": r"(\frac{m^5 n^0}{m^2})^3",
        "skeleton": [
            {"step_latex": r"\text{Apply Zero Exponent Rule in numerator: } n^0 \Rightarrow 1", "correct_rule": "EXP_04",},
            {"step_latex": r"\text{Rewrite the fraction: } (\frac{m^5}{m^2})^3", "correct_rule": None,},
            {"step_latex": r"\text{Apply Quotient Rule inside parentheses: } m^{5-2}", "correct_rule": "EXP_02",},
            {"step_latex": r"\text{Simplify inside parentheses: } (m^3)^3", "correct_rule": None,},
            {"step_latex": r"\text{Apply Power Rule: } m^{3 \cdot 3}", "correct_rule": "EXP_03",},
            {"step_latex": r"\text{Final Answer: } m^9", "correct_rule": None,},
        ],
    },
    # Problem Set 3
    {
        "title": "Practice Problem 3: Product/Power/Quotient Mix",
        "problem_latex": r"\frac{2x^3 (3x^2)^2}{x^4}",
        "skeleton": [
            {"step_latex": r"\text{Apply Power Rule to term: } (3x^2)^2 \Rightarrow 3^2 (x^2)^2 = 9x^4", "correct_rule": "EXP_03",},
            {"step_latex": r"\text{Rewrite the fraction: } \frac{2x^3 (9x^4)}{x^4}", "correct_rule": None,},
            {"step_latex": r"\text{Apply Product Rule in numerator: } (2 \cdot 9) x^{3+4}", "correct_rule": "EXP_01",},
            {"step_latex": r"\text{Simplify numerator: } \frac{18x^7}{x^4}", "correct_rule": None,},
            {"step_latex": r"\text{Apply Quotient Rule: } 18 x^{7-4}", "correct_rule": "EXP_02",},
            {"step_latex": r"\text{Final Answer: } 18x^3", "correct_rule": None,},
        ],
    },
]

# Multiple sets of test questions for rotation
ALL_TEST_SETS = [
    # Test Set 1
    {
        "questions": [
            {
                "question": r"(ab^3)^2 a^4",
                "solution_steps": [r"\text{Step 1 (Power Rule): } a^2 b^6", r"\text{Step 2 (Product Rule): } a^{2+4} b^6", r"\text{Final Answer: } a^6 b^6",],
            },
            {
                "question": r"\frac{20x^8 y^5}{5x^3 y^5}",
                "solution_steps": [r"\text{Step 1 (Quotient/Zero): } 4 x^{8-3} y^{5-5}", r"\text{Final Answer: } 4x^5",],
            },
            {
                "question": r"(m^0 n)^3",
                "solution_steps": [r"\text{Step 1 (Zero Exponent): } (1 \cdot n)^3", r"\text{Final Answer: } n^3",],
            },
            {
                "question": r"\frac{a^{10}}{a^{10}}",
                "solution_steps": [r"\text{Step 1 (Quotient/Zero): } a^{10-10} = a^0", r"\text{Final Answer: } 1",],
            },
            {
                "question": r"(3x^2)^3",
                "solution_steps": [r"\text{Step 1 (Power Rule): } 3^3 (x^2)^3", r"\text{Final Answer: } 27 x^6",],
            },
        ],
        "answers": [r"a^6 b^6", r"4x^5", r"n^3", r"1", r"27 x^6"],
    },
    # Test Set 2 (New)
    {
        "questions": [
            {
                "question": r"x^2 \cdot x^4 \cdot x",
                "solution_steps": [r"\text{Step 1 (Product Rule): } x^{2+4+1}", r"\text{Final Answer: } x^7",],
            },
            {
                "question": r"\frac{18p^7}{6p^3}",
                "solution_steps": [r"\text{Step 1 (Quotient Rule): } 3 p^{7-3}", r"\text{Final Answer: } 3p^4",],
            },
            {
                "question": r"((y^3)^2)^4",
                "solution_steps": [r"\text{Step 1 (Power Rule): } y^{3\cdot 2 \cdot 4}", r"\text{Final Answer: } y^{24}",],
            },
            {
                "question": r"(4w)^0",
                "solution_steps": [r"\text{Step 1 (Zero Exponent): } (4w)^0", r"\text{Final Answer: } 1",],
            },
            {
                "question": r"m^5 (m^3 \cdot m)",
                "solution_steps": [r"\text{Step 1 (Product Rule): } m^5 (m^{3+1}) = m^5 m^4", r"\text{Step 2 (Product Rule): } m^{5+4}", r"\text{Final Answer: } m^9",],
            },
        ],
        "answers": [r"x^7", r"3p^4", r"y^{24}", r"1", r"m^9"],
    },
    # Test Set 3 (New)
    {
        "questions": [
            {
                "question": r"(\frac{1}{z})^2 \cdot z^5",
                "solution_steps": [r"\text{Step 1 (Power Rule): } \frac{1^2}{z^2} \cdot z^5 = z^{-2} z^5", r"\text{Step 2 (Product Rule): } z^{-2+5}", r"\text{Final Answer: } z^3",],
            },
            {
                "question": r"\frac{100 a^9 b^2}{25 a^5 b^2}",
                "solution_steps": [r"\text{Step 1 (Quotient/Zero): } 4 a^{9-5} b^{2-2}", r"\text{Final Answer: } 4a^4",],
            },
            {
                "question": r"(2^3)^2 / 2^4",
                "solution_steps": [r"\text{Step 1 (Power Rule): } 2^6 / 2^4", r"\text{Step 2 (Quotient Rule): } 2^{6-4} = 2^2", r"\text{Final Answer: } 4",],
            },
            {
                "question": r"(-5)^0 + 1",
                "solution_steps": [r"\text{Step 1 (Zero Exponent): } 1 + 1", r"\text{Final Answer: } 2",],
            },
            {
                "question": r"(xy^4)^3 / x^3",
                "solution_steps": [r"\text{Step 1 (Power Rule): } x^3 y^{12} / x^3", r"\text{Step 2 (Quotient/Zero): } x^{3-3} y^{12} = 1 \cdot y^{12}", r"\text{Final Answer: } y^{12}",],
            },
        ],
        "answers": [r"z^3", r"4a^4", r"4", r"2", r"y^{12}"],
    },
]

LESSON_PAGES = {
    "1. Rules Overview": {"type": "theory_summary"},
    "2. Product Rule (Examples)": {
        "type": "rule_examples",
        "rule_id": "EXP_01",
    },
    "3. Quotient Rule (Examples)": {
        "type": "rule_examples",
        "rule_id": "EXP_02",
    },
    "4. Practice (Interactive Skeleton)": {"type": "practice_interactive"},
    "5. Test (Graded Questions)": {"type": "test_static"},
    "6. Analytics (Submissions)": {"type": "analytics_page"},
}


# -------------------------
# HELPERS
# -------------------------
def get_rule_by_id(rid):
    return next((r for r in RULES_DATA if r["id"] == rid), None)

def get_random_examples(rule_id):
    """Retrieves a random set of examples for a given rule ID from the sets."""
    sets = RULE_EXAMPLE_SETS.get(rule_id, [])
    if not sets:
        return []
        
    session_key = f"examples_{rule_id}_set_index"
        
    if session_key not in st.session_state:
        st.session_state[session_key] = random.randrange(len(sets))
            
    return sets[st.session_state[session_key]]

def get_practice_problem():
    """Retrieves a single, session-stable practice problem for the interactive section."""
    session_key = "practice_problem_index"
    
    if session_key not in st.session_state:
        st.session_state[session_key] = random.randrange(len(INTERACTIVE_PROBLEM_SETS))
        
    return INTERACTIVE_PROBLEM_SETS[st.session_state[session_key]]

def get_current_test_set():
    """Retrieves the current test set for the 'Test' page."""
    session_key = "current_test_set_index"
    
    # Initialize the index if not present
    if session_key not in st.session_state:
        st.session_state[session_key] = random.randrange(len(ALL_TEST_SETS))
        
    # Return the selected set
    return ALL_TEST_SETS[st.session_state[session_key]], st.session_state[session_key]

def rotate_test_set():
    """Increments the test set index, wrapping around if necessary."""
    current_index = st.session_state.get("current_test_set_index", 0)
    new_index = (current_index + 1) % len(ALL_TEST_SETS)
    st.session_state["current_test_set_index"] = new_index
    
    # Reset answers for the *new* test set size
    new_set_size = len(ALL_TEST_SETS[new_index]["questions"])
    st.session_state.user_test_answers = [""] * new_set_size

def normalize_answer(ans):
    """Normalizes the answer string for simple comparison."""
    # Simple normalization: remove all whitespace, convert to lowercase
    # This is a loose match for string-based math input
    return str(ans).replace(' ', '').lower().strip()

def submit_test_score(user_answers, expected_answers, total_questions):
    """Grades the user's submission and logs the score."""
    
    correct_count = 0
    graded_answers = []

    for i, user_ans in enumerate(user_answers):
        expected_ans = expected_answers[i]
        
        is_correct = normalize_answer(user_ans) == normalize_answer(expected_ans)
        
        if is_correct:
            correct_count += 1

        # Format feedback for analytics table
        graded_answers.append(f"Q{i+1}: {'✅' if is_correct else '❌'}")

    percentage = ceil((correct_count / total_questions) * 100)
    
    # Log the submission details
    st.session_state.test_submissions.append({
        "Submission Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Test Set": st.session_state["current_test_set_index"] + 1,
        "Score": f"{correct_count}/{total_questions}",
        "Percentage": f"{percentage}%",
        "Detailed Feedback": " | ".join(graded_answers)
    })
    
    # Update feedback for the user
    st.session_state.last_submission_score = f"{correct_count}/{total_questions}"
    st.session_state.show_grade_result = True
    
    # Reset answers and rotate set for the next test
    rotate_test_set()
    
    st.rerun() # Rerun to update the feedback

# -------------------------
# RENDERERS
# -------------------------
def render_rules_overview():
    st.header("Rules Overview — Exponents (Bird’s-eye)")
    st.markdown(
        "Below are the core exponent rules. Each rule shows a clean LaTeX formula, a short description, and the internal ID."
    )
    st.divider()
    for r in RULES_DATA:
        with st.container():
            st.subheader(f"{r['id']}: {r['name']}")
            st.latex(r["formula"])
            st.markdown(r["description"])
            st.caption(f"ID: `{r['id']}`")
            st.markdown("---")


def render_rule_examples(page_data):
    rid = page_data.get("rule_id")
    rule = get_rule_by_id(rid)
    
    examples = get_random_examples(rid)
    
    if rule:
        set_index = st.session_state.get(f'examples_{rid}_set_index', 0)
        st.header(f"{rule['name']} — Examples (Set #{set_index + 1})")
        st.markdown(rule["description"])
        st.latex(rule["formula"])
        st.markdown("---")
        
        if st.button(f"Generate New {rule['name']} Examples", key=f"reset_ex_{rid}"):
            del st.session_state[f"examples_{rid}_set_index"]
            st.rerun()
            
        st.subheader("Examples")
        for i, (q, a) in enumerate(examples, start=1):
            with st.container(border=True):
                st.markdown(f"**Example {i}**")
                
                st.markdown("### Problem:")
                st.latex(q)
                
                st.markdown("### Solution:")
                st.latex(a)
            st.write("")


def render_practice_interactive():
    # Get the current problem and its index for display
    problem_set_index = st.session_state.get("practice_problem_index", 0)
    INTERACTIVE_PROBLEM = get_practice_problem()
    
    st.header(f"{INTERACTIVE_PROBLEM['title']} (Problem Set #{problem_set_index + 1})")
    st.markdown(
        "Work through the skeleton of the solution. For steps that require a rule, select the rule that applies and press **Check Rule**. Correct answers advance you to the next step."
    )
    st.latex(INTERACTIVE_PROBLEM["problem_latex"])
    st.markdown("---")

    # Initialize practice session state for steps/score (scoped to the problem)
    if "practice_step" not in st.session_state:
        st.session_state.practice_step = 0
        st.session_state.practice_score = 0
        st.session_state.practice_feedback = ""
    # Reset practice step/score if the problem index changed
    elif st.session_state.get("last_problem_index") != problem_set_index:
        st.session_state.practice_step = 0
        st.session_state.practice_score = 0
        st.session_state.practice_feedback = ""
    
    # Store the current problem index to detect future changes
    st.session_state.last_problem_index = problem_set_index

    skeleton = INTERACTIVE_PROBLEM["skeleton"]
    current = st.session_state.practice_step

    # Show progress bar
    total_rule_steps = sum(1 for s in skeleton if s["correct_rule"])
    st.progress(min(1.0, st.session_state.practice_score / (total_rule_steps or 1)))

    # Render steps up to current (completed steps)
    for i, step in enumerate(skeleton):
        if i < current:
            st.markdown(f"**Step {i+1} (completed):**")
            st.latex(step["step_latex"])
            # Only show success message if it was a rule-based step
            if step["correct_rule"] is not None:
                st.success("Rule identification — completed.")
            else:
                st.info("Simplification step — completed.")
            st.markdown("---")
        elif i == current:
            st.markdown(f"**Step {i+1} (current):**")
            st.latex(step["step_latex"])

            if step["correct_rule"] is None:
                # Simplification step — allow user to continue
                if st.button("Continue (simplification)", key=f"cont_{i}"):
                    st.session_state.practice_step += 1
                    st.session_state.practice_feedback = ""
                    st.rerun()
            else:
                # Interactive: select the rule that applies
                options = ["-- Select rule --"] + [f"{r['id']} — {r['name']}" for r in RULES_DATA]
                choice = st.selectbox("Choose the rule that applies", options, key=f"sel_{i}")
                if st.button("Check Rule", key=f"check_{i}"):
                    if choice == "-- Select rule --":
                        st.session_state.practice_feedback = "Select a rule first."
                    else:
                        chosen_id = choice.split(" — ")[0]
                        if chosen_id == step["correct_rule"]:
                            st.session_state.practice_score += 1
                            st.session_state.practice_step += 1
                            st.session_state.practice_feedback = "✅ Correct — advancing to next step."
                            st.rerun()
                        else:
                            correct_rule = get_rule_by_id(step["correct_rule"])
                            st.session_state.practice_feedback = f"❌ Incorrect. Hint: review {correct_rule['name']}."
            if st.session_state.practice_feedback:
                if st.session_state.practice_feedback.startswith("✅"):
                    st.success(st.session_state.practice_feedback)
                elif st.session_state.practice_feedback.startswith("❌"):
                    st.error(st.session_state.practice_feedback)
                else:
                    st.info(st.session_state.practice_feedback)
            st.markdown("---")
            break
        else:
            st.markdown(f"**Step {i+1}: (locked yet)**")
            st.markdown("---")

    if st.session_state.practice_step >= len(skeleton):
        st.success(
            f"Practice complete — Score: {st.session_state.practice_score} / {total_rule_steps} rule-identification steps."
        )

def render_analytics_page():
    st.header("6. Analytics — Test Submission History")
    st.markdown("This section tracks your performance over time. Submissions are graded out of 5 questions.")
    st.divider()

    if st.session_state.test_submissions:
        df_submissions = pd.DataFrame(st.session_state.test_submissions)
        
        # 1. Prepare data for the chart
        # Convert Percentage string (e.g., "80%") to an integer value (80)
        df_submissions['Percentage_Value'] = df_submissions['Percentage'].str.replace('%', '').astype(int)
        
        # 2. Display the chart
        st.subheader("Performance Trend")
        st.line_chart(df_submissions, x='Submission Time', y='Percentage_Value', use_container_width=True)
        st.caption("Score Percentage Over Time")
        
        st.divider()
        
        # 3. Display the submission table
        st.subheader("Submission Details")
        st.dataframe(df_submissions.drop(columns=['Percentage_Value', 'Detailed Feedback'], errors='ignore'), 
                     hide_index=True, 
                     use_container_width=True)
        st.caption("Detailed feedback (Q1: ✅ | Q2: ❌, etc.) is stored and can be reviewed.")
    else:
        st.info("No test submissions recorded yet. Navigate to the 'Test' page to submit a test.")

def render_test_static():
    
    # Get the current test set and index
    current_test_set, set_index = get_current_test_set()
    TEST_QUESTIONS = current_test_set["questions"]
    FINAL_ANSWERS = current_test_set["answers"]
    
    st.header(f"5. Test — Set #{set_index + 1} of {len(ALL_TEST_SETS)} (5 Graded Questions)")
    st.markdown("Enter your final simplified answer for each question below. The answers are graded automatically.")
    st.divider()
    
    current_set_size = len(TEST_QUESTIONS)
    
    # Initialize user answers: this must happen whenever the test set changes size
    if 'user_test_answers' not in st.session_state or len(st.session_state.user_test_answers) != current_set_size:
        st.session_state.user_test_answers = [""] * current_set_size
        
    user_answers = st.session_state.user_test_answers
    
    # Display previous result if available (Initialized in main, used here)
    if st.session_state.show_grade_result:
        st.success(f"Test Graded! Your score is **{st.session_state.last_submission_score}**. Check the 'Analytics' tab for history. A new test set is ready!")
        # Reset flag immediately after displaying to ensure it only shows once
        st.session_state.show_grade_result = False
        
    # Use a form for submission
    with st.form("test_submission_form", clear_on_submit=False): 
        # Note: clear_on_submit=False is used because we explicitly manage state reset in submit_test_score
        
        # Collect answers
        for i, q in enumerate(TEST_QUESTIONS, start=1):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**Q{i}:**")
                st.latex(q["question"])
            
            with col2:
                # Use a specific key tied to the question index to store input
                user_answers[i-1] = st.text_input(
                    f"Enter simplified answer for Q{i}", 
                    value=user_answers[i-1],
                    key=f"q_input_{set_index}_{i}", # Key now includes the set index for proper state isolation
                    placeholder="e.g., a^6b^6, 4x^5, etc."
                )
            
            # Solution Expander (hidden during input)
            with st.expander(f"Show solution for Q{i}"):
                st.markdown("**Solution steps**")
                for step in q["solution_steps"]:
                    st.latex(step)
                st.markdown("---")
                st.info("Review: This problem required applying the key rules in the correct order to simplify the expression.")
            st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button("Grade Test and Save to Analytics")
        
        if submitted:
            # Pass the answers and expected values to the grading function
            submit_test_score(user_answers, FINAL_ANSWERS, len(TEST_QUESTIONS))


# -------------------------
# MAIN
# -------------------------
def main():
    st.title("📘 Interactive Lesson Builder — Exponents")
    
    # --- GLOBAL STATE INITIALIZATION (FIX FOR ATTRIBUTE ERROR) ---
    if 'test_submissions' not in st.session_state:
        st.session_state.test_submissions = []
    if 'current_test_set_index' not in st.session_state:
        st.session_state['current_test_set_index'] = random.randrange(len(ALL_TEST_SETS))
    
    # Initialize the feedback flags here to ensure they always exist
    if 'show_grade_result' not in st.session_state:
        st.session_state.show_grade_result = False
    if 'last_submission_score' not in st.session_state:
        st.session_state.last_submission_score = ""
    # ------------------------------------------------------------
    
    # Initialize user answers based on the current set size (this ensures size matches the set)
    current_set_size = len(ALL_TEST_SETS[st.session_state.current_test_set_index]["questions"])
    if 'user_test_answers' not in st.session_state or len(st.session_state.user_test_answers) != current_set_size:
         st.session_state.user_test_answers = [""] * current_set_size
    
    # Sidebar navigation
    page_titles = list(LESSON_PAGES.keys())
    sel = st.sidebar.radio("Lesson Navigation", page_titles, index=0)

    st.sidebar.markdown("---")
    
    # Sidebar control for Practice section reset
    if sel == "4. Practice (Interactive Skeleton)":
        if st.sidebar.button("Reset / Get New Practice Problem"):
            del st.session_state["practice_problem_index"]
            if "practice_step" in st.session_state:
                 del st.session_state.practice_step
            st.rerun()
    
    # Sidebar control for Test section reset
    if sel == "5. Test (Graded Questions)":
        if st.sidebar.button("Generate New Test Set"):
            rotate_test_set()
            st.rerun()

    st.sidebar.markdown("Flow: Rules Overview → Focused Examples → Practice → Test")

    page = LESSON_PAGES.get(sel, {})
    ptype = page.get("type", "rule_examples")

    if ptype == "theory_summary":
        render_rules_overview()
    elif ptype == "rule_examples":
        render_rule_examples(page)
    elif ptype == "practice_interactive":
        render_practice_interactive()
    elif ptype == "test_static":
        render_test_static()
    elif ptype == "analytics_page":
        render_analytics_page()
    else:
        st.error("Unknown page type.")


if __name__ == "__main__":
    main()