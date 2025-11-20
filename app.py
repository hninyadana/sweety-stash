import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

# --- CONFIGURATION & CONSTANTS ---
DATA_FILE = "sweety_stash_data.json"
PET_NAME_DEFAULT = "Sweety"

# --- CORE LOGIC CLASS ---
class SweetyStash:
    def __init__(self):
        self.data = self._load_data()
        self._initialize_defaults()
        self._check_daily_reset()

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save_data(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            st.error(f"Error saving data: {e}")

    def _initialize_defaults(self):
        # Core Budget Data
        self.data.setdefault("monthly_income", 0.0)
        self.data.setdefault("monthly_savings_goal", 0.0)
        self.data.setdefault("fixed_expenses", {}) # {name: amount}

        # Tracking Data
        self.data.setdefault("daily_expenses", []) # List of {date, category, amount, description, is_big_purchase}
        self.data.setdefault("extra_goals", {}) # {name: {target, saved}}

        # Pet/Gamification Data
        self.data.setdefault("pet_name", PET_NAME_DEFAULT)
        self.data.setdefault("saving_streak", 0)
        self.data.setdefault("last_streak_date", None)
        self.data.setdefault("daily_treat_given", False)
        self.data.setdefault("last_treat_date", None)
        self.data.setdefault("rewards_unlocked", [])

    def _check_daily_reset(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data.get("last_treat_date") != today:
            self.data["daily_treat_given"] = False
            self.data["last_treat_date"] = today
            self._save_data()

    # --- BUDGET & SETUP ---
    def set_budget(self, income, goal):
        try:
            self.data["monthly_income"] = float(income)
            self.data["monthly_savings_goal"] = float(goal)
            self._save_data()
            return True
        except ValueError:
            return False

    def set_pet_name(self, name):
        if name and name.strip():
            self.data["pet_name"] = name.strip()
            self._save_data()
            return True
        return False

    def add_fixed_expense(self, name, amount):
        try:
            if not name or not name.strip():
                 return False, "Expense name cannot be empty."
            amount_float = float(amount)
            if amount_float < 0:
                 return False, "Amount must be positive."

            self.data["fixed_expenses"][name] = amount_float
            self._save_data()
            return True, "Success"
        except ValueError:
            return False, "Invalid amount. Please enter a number."

    def remove_fixed_expense(self, name):
        if name in self.data["fixed_expenses"]:
            del self.data["fixed_expenses"][name]
            self._save_data()

    # --- DAILY TRANSACTIONS ---
    def log_expense(self, amount, category, description, is_big_purchase=False):
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return False, "Amount must be greater than zero."

            transaction = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "amount": amount_float,
                "category": category,
                "description": description,
                "is_big_purchase": is_big_purchase
            }
            self.data["daily_expenses"].append(transaction)
            self._update_streak(is_big_purchase)
            self._save_data()
            return True, "Expense logged successfully!"
        except ValueError:
            return False, "Invalid amount. Please enter a number."

    # --- GOALS ---
    def add_extra_goal(self, name, target):
        try:
            target_float = float(target)
            if not name or not name.strip():
                return False, "Goal name cannot be empty."
            if target_float <= 0:
                return False, "Target amount must be positive."

            if name not in self.data["extra_goals"]:
                self.data["extra_goals"][name] = {"target": target_float, "saved": 0.0}
                self._save_data()
                return True, f"Goal '{name}' added!"
            else:
                return False, f"Goal '{name}' already exists."
        except ValueError:
            return False, "Invalid target amount."

    def contribute_to_goal(self, goal_name, amount):
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return False, "Contribution amount must be positive."

            if goal_name in self.data["extra_goals"]:
                self.data["extra_goals"][goal_name]["saved"] += amount_float
                self._save_data()
                return True, f"Contributed ${amount_float:.2f} to {goal_name}."
            return False, "Goal not found."
        except ValueError:
            return False, "Invalid amount."

    # --- CALCULATIONS ---
    def get_financial_summary(self):
        total_income = self.data["monthly_income"]
        total_fixed = sum(self.data["fixed_expenses"].values())
        target_saving = self.data["monthly_savings_goal"]

        # Expenses for the CURRENT MONTH only
        current_month = datetime.now().strftime("%Y-%m")
        monthly_expenses = [e for e in self.data["daily_expenses"] if e["date"].startswith(current_month)]

        total_daily_spending = sum(e["amount"] for e in monthly_expenses if not e["is_big_purchase"])
        total_big_purchases = sum(e["amount"] for e in monthly_expenses if e["is_big_purchase"])

        # Calculation:
        # 1. Disposable Income = Income - Fixed Expenses - Savings Goal
        # 2. Daily Allowance = Disposable Income / 30
        disposable_income = total_income - total_fixed - target_saving
        daily_allowance = max(0, disposable_income / 30) if disposable_income > 0 else 0

        # Calculate savings status for TODAY
        today = datetime.now().strftime("%Y-%m-%d")
        todays_expenses = sum(e["amount"] for e in self.data["daily_expenses"] 
                              if e["date"] == today and not e["is_big_purchase"])

        todays_savings = daily_allowance - todays_expenses

        return {
            "monthly_income": total_income,
            "fixed_expenses": total_fixed,
            "target_saving": target_saving,
            "daily_allowance": daily_allowance,
            "todays_expenses": todays_expenses,
            "todays_savings": todays_savings,
            "total_spent_month": total_daily_spending + total_big_purchases + total_fixed
        }

    # --- GAMIFICATION ---
    def get_pet_status(self, financials):
        savings = financials["todays_savings"]
        treat_given = self.data["daily_treat_given"]
        streak = self.data["saving_streak"]

        mood = "neutral"
        message = f"{self.data['pet_name']} is waiting for you to update your spending."
        image = "🐱" 

        if savings >= 0 and financials["todays_expenses"] > 0:
            mood = "happy"
            message = f"Purrfect! You saved ${savings:.2f} today!"
            image = "😺"
        elif savings < 0:
            mood = "sad"
            message = f"Meow... You overspent by ${abs(savings):.2f}. {self.data['pet_name']} is sad."
            image = "😿"

        if treat_given:
            mood = "excited"
            message += " (Treat Received! Yum!)"
            image = "😻"

        return {"mood": mood, "message": message, "image": image, "streak": streak}

    def give_treat(self):
        financials = self.get_financial_summary()
        if financials["todays_savings"] >= 0:
            self.data["daily_treat_given"] = True
            self._save_data()
            return True
        return False

    def _update_streak(self, is_big_purchase):
        # Logic: Streak increases if you log expenses and stay within budget.
        # Big purchases don't reset streak (they are exceptions), but don't increment it either.
        if is_big_purchase:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        last_streak = self.data["last_streak_date"]

        financials = self.get_financial_summary()

        # Only process streak at end of day logic or simply check "on track" status
        # For simplicity: If you are under budget, streak is active.
        if financials["todays_savings"] >= 0:
            if last_streak != today:
                # Check if last streak was yesterday (consecutive)
                if last_streak:
                    last_date = datetime.strptime(last_streak, "%Y-%m-%d")
                    if (datetime.now() - last_date).days == 1:
                        self.data["saving_streak"] += 1
                    elif (datetime.now() - last_date).days > 1:
                        self.data["saving_streak"] = 1 # Reset
                else:
                    self.data["saving_streak"] = 1

                self.data["last_streak_date"] = today
        else:
            # Over budget breaks streak
            self.data["saving_streak"] = 0

        self._check_rewards()

    def _check_rewards(self):
        streak = self.data["saving_streak"]
        rewards = self.data["rewards_unlocked"]

        if streak >= 7 and "Weekly Spa" not in rewards:
            rewards.append("Weekly Spa")
            st.toast(f"🎉 7-Day Streak! {self.data['pet_name']} gets a Spa Day!", icon="🛁")
        if streak >= 30 and "Monthly Vacation" not in rewards:
            rewards.append("Monthly Vacation")
            st.toast(f"🎉 30-Day Streak! {self.data['pet_name']} goes on Vacation!", icon="✈️")


# --- UI RENDERER ---
def main():
    st.set_page_config(page_title="Sweety Stash", page_icon="🐾", layout="wide")

    # Initialize App Logic
    if 'app' not in st.session_state:
        st.session_state.app = SweetyStash()

    app = st.session_state.app

    # --- SIDEBAR: SETUP ---
    with st.sidebar:
        st.header("⚙️ Setup")
        pet_name = st.text_input("Pet Name", value=app.data["pet_name"])
        if st.button("Update Name"):
            app.set_pet_name(pet_name)
            st.rerun()

        st.subheader("Monthly Budget")
        # Use text_input for better control over empty/invalid states initially, 
        # though number_input is generally safer, text_input allows easier clearing.
        # We'll stick to number_input but validate the update.
        income = st.number_input("Monthly Income", value=app.data["monthly_income"], min_value=0.0)
        goal = st.number_input("Target Saving Goal", value=app.data["monthly_savings_goal"], min_value=0.0)

        if st.button("Update Budget"):
            if app.set_budget(income, goal):
                st.success("Budget Updated!")
                st.rerun()
            else:
                st.error("Invalid budget values.")

        st.divider()
        st.header("🏠 Fixed Expenses")
        with st.form("fixed_exp"):
            name = st.text_input("Expense Name (e.g., Rent)")
            amount = st.number_input("Amount", min_value=0.0)
            if st.form_submit_button("Add Fixed Expense"):
                success, msg = app.add_fixed_expense(name, amount)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.write("Current Fixed Expenses:")
        for k, v in app.data["fixed_expenses"].items():
            st.write(f"- {k}: ${v:.2f}")
            if st.button(f"Remove {k}", key=f"rem_{k}"):
                app.remove_fixed_expense(k)
                st.rerun()

    # --- MAIN PAGE ---
    st.title(f"🐾 {app.data['pet_name']}'s Sweety Stash")

    fin_summary = app.get_financial_summary()
    pet_status = app.get_pet_status(fin_summary)

    # 1. METRICS ROW
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Daily Allowance", f"${fin_summary['daily_allowance']:.2f}")
    c2.metric("Today's Spending", f"${fin_summary['todays_expenses']:.2f}")
    c3.metric("Today's Savings", f"${fin_summary['todays_savings']:.2f}", 
              delta="On Track" if fin_summary['todays_savings'] >= 0 else "Over Budget")
    c4.metric("Streak", f"{pet_status['streak']} Days")

    # 2. PET STATUS & TREATS
    st.divider()
    col_pet, col_actions = st.columns([1, 2])

    with col_pet:
        st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{pet_status['image']}</h1>", unsafe_allow_html=True)
        st.info(f"**Status:** {pet_status['message']}")

        # Treat Button
        if fin_summary['todays_savings'] >= 0:
            if st.button("🍖 Give Treat", disabled=app.data["daily_treat_given"]):
                if app.give_treat():
                    st.balloons()
                    st.rerun()
        else:
            st.warning("Save more today to give a treat!")

    with col_actions:
        st.subheader("📝 Log Daily Expense")
        with st.form("daily_exp"):
            desc = st.text_input("Description (e.g., Lunch)")
            amt = st.number_input("Amount", min_value=0.0) # Changed to allow 0 initially, logic handles > 0
            cat = st.selectbox("Category", ["Food", "Transport", "Shopping", "Entertainment", "Other"])
            is_big = st.checkbox("Big Purchase? (Won't break daily streak)", help="Use for perfume, electronics, etc.")

            if st.form_submit_button("Log Expense"):
                success, msg = app.log_expense(amt, cat, desc, is_big)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # 3. EXTRA GOALS
    st.divider()
    st.subheader("🎯 Extra Saving Goals")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.form("new_goal"):
            g_name = st.text_input("Goal Name (e.g., Trip to Paris)")
            g_target = st.number_input("Target Amount", min_value=1.0)
            if st.form_submit_button("Set Goal"):
                success, msg = app.add_extra_goal(g_name, g_target)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with col_g2:
        if app.data["extra_goals"]:
            goal_name = st.selectbox("Select Goal to Contribute", list(app.data["extra_goals"].keys()))
            contrib_amt = st.number_input("Contribution Amount", min_value=1.0)
            if st.button("Contribute from Main Savings"):
                success, msg = app.contribute_to_goal(goal_name, contrib_amt)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # Display Goal Progress
    if app.data["extra_goals"]:
        for name, details in app.data["extra_goals"].items():
            prog = min(1.0, details["saved"] / details["target"])
            st.write(f"**{name}**: ${details['saved']:.2f} / ${details['target']:.2f}")
            st.progress(prog)

    # 4. REPORTS (Basic History)
    st.divider()
    with st.expander("📜 View Transaction History"):
        if app.data["daily_expenses"]:
            df = pd.DataFrame(app.data["daily_expenses"])
            st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
        else:
            st.write("No transactions yet.")

if __name__ == "__main__":
    main()
