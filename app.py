import streamlit as st
import json
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="TrackWise - AI Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_expenses():
    if os.path.exists("outputs/expenses.json"):
        with open("outputs/expenses.json", "r") as f:
            return json.load(f)
    return []

def load_crew_analysis():
    if os.path.exists("outputs/crew_analysis.json"):
        with open("outputs/crew_analysis.json", "r") as f:
            return json.load(f)
    return None

expenses = load_expenses()
crew_data = load_crew_analysis()

st.title("💰 TrackWise - AI Expense Tracker")
st.markdown("*Smart expense tracking powered by AI agents*")
st.markdown("---")

page = st.sidebar.selectbox(
    "📍 Navigate",
    ["🏠 Home", "📊 Dashboard", "📋 Detailed View", "🤖 AI Insights", "💰 Budget Tracker"]
)

if page == "🏠 Home":
    st.header("🏠 Home")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📸 Upload Receipt")
        uploaded_file = st.file_uploader(
            "Choose receipt image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a receipt image to extract data"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Receipt", width=400)

            if st.button("🔍 Scan Receipt", type="primary"):
                import subprocess, sys, time
                os.makedirs("images", exist_ok=True)
                save_path = os.path.join("images", uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                ocr_result = subprocess.run(
                    [sys.executable, "extract_data.py"],
                    capture_output=True,
                    text=True
                )

                if ocr_result.returncode != 0:
                    st.error("❌ OCR failed")
                    st.code(ocr_result.stderr)
                    st.stop()

                ai_result = subprocess.run(
                    [sys.executable, "run.py"],
                    capture_output=True,
                    text=True
                )

                if ai_result.returncode != 0:
                    st.error("❌ AI Analysis failed")
                    st.code(ai_result.stderr)
                    st.stop()

                st.success("✅ Receipt scanned + AI analysis updated!")
                time.sleep(1)
                st.rerun()

    
    with col2:
        st.subheader("📊 Quick Stats")
        
        if expenses:
            total = sum(e.get('total', 0) or 0 for e in expenses)
            st.metric("Total Spent", f"₹{total:,.2f}")
            st.metric("Total Receipts", len(expenses))
            st.metric("Average Expense", f"₹{total/len(expenses):,.2f}")
        else:
            st.warning("No expenses yet")
    
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.switch_page
    
    with col2:
        if st.button("🤖 Run AI Analysis", use_container_width=True):
            st.info("Navigate to AI Insights page")
    
    with col3:
        if st.button("💰 Check Budget", use_container_width=True):
            st.info("Navigate to Budget Tracker")

elif page == "📊 Dashboard":
    st.header("📊 Expense Dashboard")
    
    if not expenses:
        st.warning("⚠️ No expenses found. Upload receipts to get started!")
        st.stop()
    
    total_spent = sum(e.get('total', 0) or 0 for e in expenses)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Spent", f"₹{total_spent:,.2f}")
    col2.metric("🧾 Receipts", len(expenses))
    col3.metric("📊 Average", f"₹{total_spent/len(expenses):,.2f}")
    
    valid_expenses = [e for e in expenses if e.get('total')]
    if valid_expenses:
        col4.metric("🔝 Highest", f"₹{max(e['total'] for e in valid_expenses):,.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Spending by Merchant")
        
        merchant_totals = {}
        for e in expenses:
            merchant = e.get('merchant', 'Unknown')
            total = e.get('total', 0) or 0
            merchant_totals[merchant] = merchant_totals.get(merchant, 0) + total
        
        merchant_df = pd.DataFrame([
            {'Merchant': k, 'Amount': v}
            for k, v in sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        ])
        
        if not merchant_df.empty:
            fig = px.bar(
                merchant_df,
                x='Amount',
                y='Merchant',
                orientation='h',
                title='Top 10 Merchants by Spending'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Spending Distribution")
        
        if crew_data and 'analysis' in crew_data:
            by_category = crew_data['analysis'].get('by_category', {})
            
            if by_category:
                cat_df = pd.DataFrame([
                    {'Category': k, 'Amount': v}
                    for k, v in by_category.items()
                ])
                
                fig = px.pie(
                    cat_df,
                    values='Amount',
                    names='Category',
                    title='Spending by Category'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Run AI Analysis to see category breakdown")
        else:
            st.info("Run AI Analysis to see category breakdown")
    
    st.markdown("---")
    st.subheader("📋 Recent Transactions")
    
    df = pd.DataFrame(expenses)
    if not df.empty:
        display_df = df[['merchant', 'total', 'date', 'image_file']].copy()
        display_df.columns = ['Merchant', 'Amount (₹)', 'Date', 'Receipt']
        display_df = display_df.sort_values('Date', ascending=False).head(15)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

elif page == "📋 Detailed View":
    st.header("📋 Detailed Category Analysis")
    
    if not crew_data:
        st.warning("⚠️ No analysis data found. Run AI Analysis first!")
        if st.button("🤖 Run AI Analysis Now"):
            st.info("Navigate to AI Insights page to run analysis")
        st.stop()
    
    analysis = crew_data.get('analysis', {})
    categorization = crew_data.get('categorization', {})
    
    total_spent = analysis.get('total_spent', 0)
    by_category = analysis.get('by_category', {})
    
    st.subheader(f"💰 Total Spending: ₹{total_spent:,.2f}")
    st.markdown("---")
    
    if by_category:
        st.subheader("📊 Category Breakdown")
        
        category_data = []
        for category, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            
            receipts_in_category = [
                img for img, data in categorization.items()
                if data.get('category') == category
            ]
            
            category_data.append({
                'Category': category,
                'Amount (₹)': f"₹{amount:,.2f}",
                'Percentage': f"{percentage:.1f}%",
                'Receipts': len(receipts_in_category)
            })
        
        cat_summary_df = pd.DataFrame(category_data)
        
        st.dataframe(
            cat_summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Amount (₹)": st.column_config.TextColumn("Amount", width="medium"),
                "Percentage": st.column_config.TextColumn("% of Total", width="small"),
                "Receipts": st.column_config.NumberColumn("# Receipts", width="small")
            }
        )
        
        st.markdown("---")
        st.subheader("🔍 Detailed Breakdown by Category")
        
        selected_category = st.selectbox(
            "Select category to view details",
            options=sorted(by_category.keys())
        )
        
        if selected_category:
            receipts_in_cat = [
                (img, data) for img, data in categorization.items()
                if data.get('category') == selected_category
            ]
            
            st.markdown(f"### {selected_category}")
            st.write(f"**Total:** ₹{by_category[selected_category]:,.2f}")
            st.write(f"**Number of receipts:** {len(receipts_in_cat)}")
            
            receipt_details = []
            for img, cat_data in receipts_in_cat:
                expense = next((e for e in expenses if e['image_file'] == img), None)
                if expense:
                    receipt_details.append({
                        'Receipt': img,
                        'Merchant': expense.get('merchant', 'Unknown'),
                        'Amount': f"₹{expense.get('total', 0) or 0:.2f}",
                        'Date': expense.get('date', 'N/A'),
                        'Confidence': f"{cat_data.get('confidence', 0)}%"
                    })
            
            if receipt_details:
                detail_df = pd.DataFrame(receipt_details)
                st.dataframe(
                    detail_df,
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("No category data available")

elif page == "🤖 AI Insights":
    st.header("🤖 AI-Powered Insights")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Get intelligent analysis of your spending powered by AI agents")
    
    with col2:
        if st.button("🚀 Run AI Analysis", type="primary", use_container_width=True):
            with st.spinner("AI agents analyzing your spending..."):
                import subprocess
                result = subprocess.run(['python', 'run.py'], capture_output=True, text=True)
                
                if result.returncode == 0:
                    st.success("✅ Analysis complete!")
                    st.rerun()
                else:
                    st.error("❌ Analysis failed. Check console for errors.")
    
    if not crew_data:
        st.info("👆 Click 'Run AI Analysis' to get AI-powered insights about your spending")
        st.stop()
    
    st.markdown("---")
    
    analysis = crew_data.get('analysis', {})
    advice = crew_data.get('advice', {})
    
    st.subheader("📊 Spending Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Financial Summary")
        total = analysis.get('total_spent', 0)
        st.metric("Total Spent", f"₹{total:,.2f}")
        
        by_category = analysis.get('by_category', {})
        if by_category:
            st.markdown("#### Top Categories:")
            for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]:
                pct = (amt / total * 100) if total > 0 else 0
                st.write(f"**{cat}:** ₹{amt:,.2f} ({pct:.1f}%)")
    
    with col2:
        st.markdown("### 🔍 Key Insights")
        insights = analysis.get('insights', [])
        if insights:
            for i, insight in enumerate(insights, 1):
                st.info(f"**{i}.** {insight}")
        else:
            st.write("No insights available")
        
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            st.markdown("#### ⚠️ Anomalies Detected:")
            for anomaly in anomalies:
                st.warning(anomaly)
    
    st.markdown("---")
    st.subheader("💡 Budget Advice")
    
    budget_status = advice.get('budget_status', 'N/A')
    
    if 'over' in budget_status.lower():
        st.error(f"📈 Status: {budget_status.title()}")
    elif 'under' in budget_status.lower():
        st.success(f"📉 Status: {budget_status.title()}")
    else:
        st.info(f"📊 Status: {budget_status.title()}")
    
    tips = advice.get('tips', [])
    if tips:
        st.markdown("### 💡 Money-Saving Tips")
        for i, tip in enumerate(tips, 1):
            st.markdown(f"**{i}.** {tip}")
    
    quick_win = advice.get('quick_win')
    if quick_win:
        st.success(f"⚡ **Quick Win:** {quick_win}")
    
    positive = advice.get('positive')
    if positive:
        st.balloons()
        st.success(f"✨ {positive}")

elif page == "💰 Budget Tracker":
    st.header("💰 Budget Management")
    
    budget_file = "outputs/budget_settings.json"
    
    if os.path.exists(budget_file):
        with open(budget_file, "r") as f:
            budget_settings = json.load(f)
    else:
        budget_settings = {"monthly_budget": 10000}
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        monthly_budget = st.number_input(
            "Set Monthly Budget (₹)",
            value=budget_settings.get('monthly_budget', 10000),
            step=500,
            min_value=0
        )
        
        if st.button("💾 Save Budget"):
            budget_settings['monthly_budget'] = monthly_budget
            with open(budget_file, "w") as f:
                json.dump(budget_settings, f)
            st.success("Budget saved!")
    
    with col2:
        st.metric("Monthly Budget", f"₹{monthly_budget:,.2f}")
    
    if expenses:
        total_spent = sum(e.get('total', 0) or 0 for e in expenses)
        remaining = monthly_budget - total_spent
        progress = (total_spent / monthly_budget * 100) if monthly_budget > 0 else 0
        
        st.markdown("---")
        st.subheader("📊 Budget Progress")
        
        st.progress(min(progress / 100, 1.0))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Spent", f"₹{total_spent:,.2f}")
        col2.metric("Remaining", f"₹{remaining:,.2f}")
        col3.metric("Progress", f"{progress:.1f}%")
        
        if progress >= 100:
            st.error("⚠️ You've exceeded your monthly budget!")
        elif progress >= 80:
            st.warning("⚠️ You've used 80% of your budget!")
        elif progress >= 50:
            st.info("📊 You're halfway through your budget")
        else:
            st.success("✅ You're within budget")
        
        st.markdown("---")
        
        if crew_data and 'analysis' in crew_data:
            by_category = crew_data['analysis'].get('by_category', {})
            
            if by_category:
                st.subheader("📊 Spending by Category")
                
                for category, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                    cat_pct = (amount / total_spent * 100) if total_spent > 0 else 0
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"**{category}**")
                    col2.write(f"₹{amount:,.2f}")
                    col3.write(f"{cat_pct:.1f}%")
                    
                    st.progress(cat_pct / 100)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Statistics")
if expenses:
    st.sidebar.metric("Total Expenses", len(expenses))
    total = sum(e.get('total', 0) or 0 for e in expenses)
    st.sidebar.metric("Total Amount", f"₹{total:,.2f}")
else:
    st.sidebar.info("No data yet")