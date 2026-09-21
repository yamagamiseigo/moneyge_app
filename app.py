import streamlit as st

st.title("💰 借入管理アプリ (Streamlit版)")

st.write("スマホからも確認できる簡易的な管理画面です。")

# 入力フォームの例
st.subheader("新しい借入の追加")
with st.form("debt_form"):
  lender = st.text_input("借入先（例：銀行A）")
  balance = st.number_input("現在残高（円）", min_value=0, step=10000)
  interest_rate = st.number_input(
      "金利（%）", min_value=0.0, max_value=100.0, step=0.1
  )

  submitted = st.form_submit_button("登録する")
  if submitted:
    st.success(
        f"「{lender}」のデータを登録しました！（残高: {balance:,}円, 金利:"
        f" {interest_rate}%）"
    )
