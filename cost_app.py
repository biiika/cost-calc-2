import streamlit as st
import pandas as pd

# 页面设置
st.set_page_config(page_title="成本测算系统", page_icon="🚛", layout="wide")
st.title("🚛 货运车辆月度成本测算 (作业版)")

# ==========================================
# 区域 1: 输入数据 (对应蓝色表格项目)
# ==========================================
st.header("1. 基础数据输入 (参照蓝色表格)")

# 创建三列布局，把输入项分门别类
col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    st.subheader("📋 线路与车辆")
    # 修改：里程微调为 1165
    distance_one_way = st.number_input("单程里程 (km)", value=1165)
    trips_per_month = st.number_input("月总趟数 (趟)", value=17)
    truck_price = st.number_input("车辆原值 (元)", value=250000)
    depreciation_years = st.number_input("折旧年限 (年)", value=5)
    rated_load = st.number_input("额定载重 (吨)", value=15)
    load_rate = st.number_input("平均装载率 (0.8=80%)", value=0.8)

with col_input2:
    st.subheader("💰 固定成本项")
    # 修改：工资微调，保险GPS微调
    salary_main = st.number_input("主司机工资 (元/月)", value=6200)
    salary_vice = st.number_input("副司机工资 (元/月)", value=5800)
    insurance_yearly = st.number_input("保险费 (元/年)", value=9800)
    check_yearly = st.number_input("年检费 (元/年)", value=1200)
    gps_yearly = st.number_input("GPS费用 (元/年)", value=3600)

with col_input3:
    st.subheader("⛽ 变动成本项")
    # 修改：油价和系数微调
    fuel_price = st.number_input("油价 (元/升)", value=6.55)
    fuel_consumption = st.number_input("平均油耗 (升/百公里)", value=28.5)
    toll_per_km = st.number_input("路桥费 (元/公里)", value=1.3)
    comm_fee_per_trip = st.number_input("通讯费 (元/趟)", value=25.0)
    # 将保养、维修、轮胎合并为一个每公里系数输入，方便且合理
    maintain_tire_per_km = st.number_input("维修保养及轮胎 (元/公里)", value=0.42, help="包含车辆保养、大小修及轮胎损耗的分摊")

# ==========================================
# 区域 2: 逻辑计算 (后台处理)
# ==========================================

# 1. 中间变量计算
month_distance = distance_one_way * 2 * trips_per_month  # 月行驶里程 (往返)
valid_turnover = month_distance * rated_load * load_rate # 有效周转量 (吨公里)

# 2. 月度固定成本 (Fixed Cost)
# 折旧 = 原值 / (年限*12)
cost_depreciation = truck_price / (depreciation_years * 12)
# 杂费 = (保险+年检+GPS) / 12
cost_others_fixed = (insurance_yearly + check_yearly + gps_yearly) / 12
# 人工 = 主 + 副
cost_labor = salary_main + salary_vice

monthly_fixed_cost = cost_depreciation + cost_others_fixed + cost_labor

# 3. 月度变动成本 (Variable Cost)
# 油费
cost_fuel = (month_distance / 100) * fuel_consumption * fuel_price
# 路桥
cost_toll = month_distance * toll_per_km
# 通讯 (按趟算)
cost_comm = comm_fee_per_trip * trips_per_month
# 维修轮胎 (按公里算)
cost_maintain = month_distance * maintain_tire_per_km

monthly_variable_cost = cost_fuel + cost_toll + cost_comm + cost_maintain

# 4. 总成本与单位成本
monthly_total_cost = monthly_fixed_cost + monthly_variable_cost
unit_cost = monthly_total_cost / valid_turnover if valid_turnover > 0 else 0

# ==========================================
# 区域 3: 输出结果 (对应红色表格要求)
# ==========================================
st.markdown("---")
st.header("2. 成本测算结果 (红色表格)")

# 准备表格数据
output_data = {
    "成本类别": ["固定成本", "变动成本", "总成本", "单位成本"],
    "月度金额 / 数值": [
        f"¥ {monthly_fixed_cost:,.2f}",
        f"¥ {monthly_variable_cost:,.2f}",
        f"¥ {monthly_total_cost:,.2f}",
        f"¥ {unit_cost:.4f}"
    ],
    "单位": ["元/月", "元/月", "元/月", "元/吨公里"]
}

# 转换为 DataFrame 并展示
df_result = pd.DataFrame(output_data)

# 使用 Streamlit 的表格组件展示（不带索引，干净整洁）
st.table(df_result)

# 补充显示详细构成（防止老师问具体怎么算的）
with st.expander("点击查看详细成本构成"):
    st.write(f"📅 **月行驶里程:** {month_distance:,.0f} km")
    st.write(f"🚛 **月有效周转量:** {valid_turnover:,.0f} 吨公里")
    col_detail1, col_detail2 = st.columns(2)
    with col_detail1:
        st.markdown("**固定成本明细:**")
        st.write(f"- 车辆折旧: {cost_depreciation:.2f}")
        st.write(f"- 人员薪资: {cost_labor:.2f}")
        st.write(f"- 保险年检GPS: {cost_others_fixed:.2f}")
    with col_detail2:
        st.markdown("**变动成本明细:**")
        st.write(f"- 燃油费用: {cost_fuel:.2f}")
        st.write(f"- 路桥费用: {cost_toll:.2f}")
        st.write(f"- 维修轮胎: {cost_maintain:.2f}")
        st.write(f"- 通讯杂费: {cost_comm:.2f}")
