import streamlit as st

# 页面设置
st.set_page_config(page_title="成本计算器", page_icon="🧮")
st.title("🧮 货运成本纯计算器")
st.caption("作业要求：月度数据基础 | 油车模型 | 纯数据输出")

# --- 第一步：输入数据 (Input) ---
st.header("1. 输入基础参数")
col1, col2 = st.columns(2)

with col1:
    st.subheader("运营数据")
    # 为了避免雷同，你可以微调这里的 value 默认值
    distance_one_way = st.number_input("单程距离 (km)", value=1155.0)
    trips_per_month = st.number_input("月单边总趟数", value=17.0)
    # 自动算出月里程，方便核对
    month_dist = distance_one_way * 2 * trips_per_month
    st.info(f"👉 自动计算月里程: {month_dist} km")
    
    st.subheader("车辆参数")
    truck_price = st.number_input("车辆购置价 (元)", value=250000.0)
    depreciation_years = st.number_input("折旧年限 (年)", value=5.0)
    rated_load = st.number_input("额定载重 (吨)", value=15.0)
    load_rate = st.number_input("平均装载率 (0.8=80%)", value=0.8)

with col2:
    st.subheader("固定支出 (年/月)")
    insurance_yearly = st.number_input("年保险费 (元/年)", value=10000.0)
    check_yearly = st.number_input("年检费 (元/年)", value=1000.0)
    gps_yearly = st.number_input("GPS费用 (元/年)", value=4000.0)
    driver_salary = st.number_input("司机月总工资 (元/月)", value=12000.0)

    st.subheader("变动支出单价")
    fuel_price = st.number_input("油价 (元/升)", value=6.45)
    fuel_consumption = st.number_input("百公里油耗 (L)", value=28.0)
    toll_per_km = st.number_input("平均路桥费 (元/km)", value=1.3)
    # 包含维修、保养、轮胎的每公里分摊
    maintenance_per_km = st.number_input("维修保养轮胎系数 (元/km)", value=0.39)

# --- 第二步：后台计算 (Logic) ---

# 1. 固定成本 (FC) = 折旧(月) + 杂费(月) + 工资
depreciation_month = truck_price / (depreciation_years * 12)
others_month = (insurance_yearly + check_yearly + gps_yearly) / 12
fc_month = depreciation_month + others_month + driver_salary

# 2. 变动成本 (VC) = 油费 + 路桥 + 维修
# 油费 = (月里程 / 100) * 油耗 * 油价
fuel_cost = (month_dist / 100) * fuel_consumption * fuel_price
toll_cost = month_dist * toll_per_km
maint_cost = month_dist * maintenance_per_km
vc_month = fuel_cost + toll_cost + maint_cost

# 3. 总成本 (TC)
tc_month = fc_month + vc_month

# 4. 单位成本 (Unit Cost)
# 周转量 = 里程 * 载重 * 装载率
turnover = month_dist * rated_load * load_rate
if turnover > 0:
    unit_cost = tc_month / turnover
else:
    unit_cost = 0.0

# --- 第三步：输出结果 (Output) ---
st.markdown("---")
st.header("2. 测算结果")

# 使用原生的表格展示，没有任何图表
result_data = {
    "测算指标": ["固定成本 (月)", "变动成本 (月)", "总成本 (月)", "单位成本 (元/吨公里)"],
    "金额 (元)": [
        f"{fc_month:,.2f}", 
        f"{vc_month:,.2f}", 
        f"{tc_month:,.2f}", 
        f"{unit_cost:.4f}"
    ],
    "备注": [
        "含折旧、保险、工资", 
        "含油费、路桥、维修", 
        "固定 + 变动", 
        "总成本 ÷ (里程×载重×装载率)"
    ]
}

st.table(result_data)

# 如果你需要直接复制数据，这里提供纯文本显示
with st.expander("点击查看可复制的纯文本数据"):
    st.text(f"""
    详细数据报告：
    -------------------------
    1. 月行驶里程: {month_dist} km
    2. 月固定成本: {fc_month:.2f} 元
    3. 月变动成本: {vc_month:.2f} 元
    4. 月总成本:   {tc_month:.2f} 元
    5. 单位成本:   {unit_cost:.4f} 元/吨公里
    -------------------------
    计算参数检查：
    - 油费占比: {fuel_cost/tc_month:.1%}
    - 路桥占比: {toll_cost/tc_month:.1%}
    """)
