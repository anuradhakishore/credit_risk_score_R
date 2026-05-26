import streamlit as st
import requests

st.set_page_config(page_title="Credit Risk App", layout="wide")

st.title("Credit Risk Prediction App")

api_url = "http://localhost:8000/predict"


# ---------------- SESSION STATE ----------------

if "predicted" not in st.session_state:
    st.session_state.predicted = False

if "result" not in st.session_state:
    st.session_state.result = None


def reset_form():
    st.session_state.predicted = False
    st.session_state.result = None


def clear_prediction():
    st.session_state.predicted = False
    st.session_state.result = None


def get_value(x):
    if isinstance(x, list):
        return x[0]
    return x


# ---------------- UI ----------------

left, right = st.columns([1, 1])

with left:
    st.subheader("Input Parameters / Customer Details")

    disabled_flag = st.session_state.predicted

    revolving_utilization = st.number_input(
        "Revolving Utilization",
        min_value=0.0,
        max_value=5.0,
        value=0.45,
        disabled=disabled_flag,
        on_change=clear_prediction,
        key="revolving_utilization"
    )

    age = st.number_input(
        "Age",
        value=45,
        disabled=disabled_flag,
        on_change=clear_prediction,
         key="age"
    )

    debt_ratio = st.number_input(
        "Debt Ratio",
        min_value=0.0,
        max_value=5.0,
        value=0.35,
        disabled=disabled_flag,
        on_change=clear_prediction,
        key="debt_ratio"
    )

    past_due_30_59 = st.number_input(
        "30-59 Days Past Due",
        min_value=0,
        max_value=20,
        value=0,
        disabled=disabled_flag,
        on_change=clear_prediction,
        key="past_due_30_59"
    )

    monthly_income = st.number_input(
        "Monthly Income",
        min_value=0,
        value=6000,
        disabled=disabled_flag,
        on_change=clear_prediction,
        key="monthly_income"
    )

    open_credit_lines = st.number_input(
        "Open Credit Lines and Loans",
        min_value=0,
        max_value=50,
        value=8,
        disabled=disabled_flag,
        on_change=clear_prediction,
        key="open_credit_lines"
    )

    times_90_late = st.number_input(
        "Number of Times 90 Days Late",
        min_value=0,
        max_value=20,
        value=0,
        disabled=disabled_flag,
        on_change=clear_prediction,
        key="times_90_late"
    )

    real_estate_loans = st.number_input(
        "Real Estate Loans or Lines",
        min_value=0,
        max_value=20,
        value=1,
        disabled=disabled_flag,
        on_change=clear_prediction,

    )

    past_due_60_89 = st.number_input(
        "60-89 Days Past Due",
        min_value=0,
        max_value=20,
        value=0,
        disabled=disabled_flag,
        on_change=clear_prediction,

    )

    dependents = st.number_input(
        "Number of Dependents",
        min_value=0,
        max_value=20,
        value=2,
        disabled=disabled_flag,
        on_change=clear_prediction,
         key="dependents"       
    )

# Validation
errors = []

if age < 18 or age > 100:
    errors.append("Age must be between 18 and 100.")

if revolving_utilization < 0 or revolving_utilization > 5:
    errors.append("Revolving Utilization must be between 0 and 5.")

if debt_ratio < 0 or debt_ratio > 5:
    errors.append("Debt Ratio must be between 0 and 5.")

if monthly_income < 0:
    errors.append("Monthly Income cannot be negative.")

if open_credit_lines < 0 or open_credit_lines > 50:
    errors.append("Open Credit Lines must be between 0 and 50.")

if times_90_late < 0 or times_90_late > 20:
    errors.append("90 Days Late must be between 0 and 20.")

if real_estate_loans < 0 or real_estate_loans > 20:
    errors.append("Real Estate Loans must be between 0 and 20.")

if past_due_30_59 < 0 or past_due_30_59 > 20:
    errors.append("30-59 Days Past Due must be between 0 and 20.")

if past_due_60_89 < 0 or past_due_60_89 > 20:
    errors.append("60-89 Days Past Due must be between 0 and 20.")

if dependents < 0 or dependents > 20:
    errors.append("Dependents must be between 0 and 20.")

has_errors = len(errors) > 0

if has_errors:
    st.session_state.result = None
    st.session_state.predicted = False



# ---------------- RESULT / PREDICT SECTION ----------------

# ---------------- RESULT / PREDICT SECTION ----------------

with right:
    st.subheader("Prediction Result")

    if st.session_state.predicted:
        st.button("New Data Entry", on_click=reset_form)

    if has_errors:
        st.error("Please fix input errors before prediction:")
        for err in errors:
            st.write(f"- {err}")

    predict_button = st.button(
        "Predict",
        disabled=has_errors or st.session_state.predicted
    )

    if predict_button:
        data = {
            "RevolvingUtilizationOfUnsecuredLines": revolving_utilization,
            "age": age,
            "NumberOfTime30_59DaysPastDueNotWorse": past_due_30_59,
            "DebtRatio": debt_ratio,
            "MonthlyIncome": monthly_income,
            "NumberOfOpenCreditLinesAndLoans": open_credit_lines,
            "NumberOfTimes90DaysLate": times_90_late,
            "NumberRealEstateLoansOrLines": real_estate_loans,
            "NumberOfTime60_89DaysPastDueNotWorse": past_due_60_89,
            "NumberOfDependents": dependents
        }

        try:
            response = requests.post(api_url, json=data, timeout=10)

            if response.status_code == 200:
                st.session_state.result = response.json()
                st.session_state.predicted = True
                st.rerun()

            else:
                st.error("API error")
                st.write(response.text)
                st.session_state.result = None
                st.session_state.predicted = False

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to API.")
            st.session_state.result = None
            st.session_state.predicted = False

        except requests.exceptions.Timeout:
            st.error("API timeout.")
            st.session_state.result = None
            st.session_state.predicted = False

    if st.session_state.predicted and st.session_state.result is not None:
        result = st.session_state.result

        prob = float(get_value(result["default_probability"]))
        pred_class_raw = str(get_value(result["predicted_class"]))
        cutoff = float(get_value(result["cutoff_used"]))
        risk_band = str(get_value(result["risk_band"]))

        pred_class = "Default" if pred_class_raw == "1" else "No Default"

        if prob < 0.10:
            decision = "APPROVE"
            interpretation = "Low chance of default."
            recommendation = "Proceed with standard approval."

        elif prob < cutoff:
            decision = "MANUAL REVIEW"
            interpretation = "Moderate risk detected."
            recommendation = "Review before approval."

        elif prob < 0.50:
            decision = "HIGH RISK REVIEW"
            interpretation = "Elevated repayment risk."
            recommendation = "Apply stricter review."

        else:
            decision = "DECLINE / ESCALATE"
            interpretation = "High chance of default."
            recommendation = "Approval not recommended."

        st.success("Prediction completed")

        st.subheader("Model Output")
        st.metric("Default Probability", f"{prob:.2%}")
        st.metric("Predicted Class", pred_class)
        st.metric("Cutoff Used", f"{cutoff:.2f}")
        st.metric("Risk Band", risk_band)

        st.subheader("Final Interpretation")
        st.write(f"**Credit Decision:** {decision}")
        st.write(f"**Meaning:** {interpretation}")
        st.write(f"**Recommended Action:** {recommendation}")