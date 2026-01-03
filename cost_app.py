import streamlit as st
import pandas as pd

# 页面配置
st.set_page_config(page_title="物流成本精细化测算", page_icon="🚛", layout="wide")
st.title("🚛 货运车辆月度成本精细化测算")

# ==========================================
# 区域 1: 参数输入 (Input)
# ==========================================
st.markdown("### 1. 基础参数设置")

# --- 第一组：线路与运营 ---
with st.expander("A. 线路与车辆运营 (点击展开)", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        distance_one_way = st.number_input("单程里程 (km)", value=1155)
    with col2:
        trips_per_month = st.number_input("月总趟数 (趟)", value=17)
    with col3:
        rated_load = st.number_input("车辆额定载重 (吨)", value=15)
    with col4:
        load_rate = st.number_input("平均装载率 (0.8=80%)", value=0.8)
    
    # 自动计算显示月度里程
    month_distance = distance_one_way * 2 * trips_per_month
    st.info(f"📊 预计月行驶总里程: **{month_distance} km** (包含去程与回程)")

# --- 第二组：固定成本参数 ---
with st.expander("B. 固定成本参数 (工资/保险/折旧等)", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        salary_main = st.number_input("主司机月工资 (元)", value=6000)
        salary_vice = st.number_input("副司机月工资 (元)", value=6000)
    with c2:
        insurance_yearly = st.number_input("商业险及交强险 (元/年)", value=10000)
        check_yearly = st.number_input("年检费 (元/年)", value=1000)
        gps_yearly = st.number_input("GPS费用 (元/年)", value=4000)
    with c3:
        truck_price = st.number_input("车辆购置原值 (元)", value=250000)
        depreciation_years = st.number_input("折旧年限 (年)", value=5)

# --- 第三组：变动成本参数 ---
with st.expander("C. 变动成本参数 (油耗/路桥/维修/轮胎)", expanded=True):
    st.markdown("**1. 燃油与路桥**")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        fuel_price = st.number_input("当前油价 (元/升)", value=6.45)
    with v2:
        # 分开去程回程油耗
        fuel_cons_full = st.number_input("去程(满载)油耗 (L/100km)", value=30.0)
    with v3:
        fuel_cons_empty = st.number_input("回程(空载)油耗 (L/100km)", value=25.0)
    with v4:
        toll_per_km = st.number_input("路桥费 (元/km)", value=1.3)
    
    st.markdown("**2. 维修与轮胎 (按实际工况计算)**")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        # 通讯费
        comm_main = st.number_input("主司机通讯费 (元/趟)", value=20)
        comm_vice = st.number_input("副司机通讯费 (元/趟)", value=5)
    with m2:
        # 保养
        maint_cost_once = st.number_input("单次保养费用 (元)", value=1500)
        maint_interval = st.number_input("保养间隔里程 (km)", value=15000)
    with m3:
        # 维修
        repair_minor_km = st.number_input("小修成本系数 (元/km)", value=0.1)
        repair_major_cost = st.number_input("大修费用预估 (元)", value=4000)
        repair_major_interval = st.number_input("大修间隔里程 (km)", value=200000)
    with m4:
        # 轮胎
        tire_price = st.number_input("单条轮胎价格 (元)", value=1000)
        tire_count = st.number_input("全车轮胎数量 (个)", value=10)
        tire_life = st.number_input("轮胎使用寿命 (km)", value=60000)

# ==========================================
# 区域 2: 核心逻辑计算
# ==========================================

# 1. 基础里程拆分
dist_outbound = distance_one_way * trips_per_month # 去程总里程
dist_return = distance_one_way * trips_per_month   # 回程总里程
dist_total = dist_outbound + dist_return           # 月总里程

# 2. 逐项计算月度成本
# --- 固定成本 ---
cost_gps = gps_yearly / 12
cost_check = check_yearly / 12
cost_insurance = insurance_yearly / 12
cost_depreciation = truck_price / (depreciation_years * 12)
# 司机工资直接取输入值

# --- 变动成本 ---
# 油费：去程
cost_fuel_out = (dist_outbound / 100) * fuel_cons_full * fuel_price
# 油费：回程
cost_fuel_in = (dist_return / 100) * fuel_cons_empty * fuel_price
# 路桥费
cost_toll = dist_total * toll_per_km
# 通讯费 (按趟数 * (主+副))
cost_comm = trips_per_month * (comm_main + comm_vice)
# 保养费 (月里程 / 间隔 * 单价)
cost_maint = (dist_total / maint_interval) * maint_cost_once
# 小修费
cost_repair_minor = dist_total * repair_minor_km
# 大修费 (月里程 / 间隔 * 单价)
cost_repair_major = (dist_total / repair_major_interval) * repair_major_cost
# 轮胎费 (月里程 / 寿命 * 单价 * 数量)
cost_tires = (dist_total / tire_life) * tire_price * tire_count

# 3. 汇总
total_fixed = salary_main + salary_vice + cost_insurance + cost_check + cost_gps + cost_depreciation
total_variable = cost_fuel_out + cost_fuel_in + cost_toll + cost_comm + cost_repair_major + cost_repair_minor + cost_tires + cost_maint
total_cost = total_fixed + total_variable

# 单位成本
valid_turnover = dist_total * rated_load * load_rate
unit_cost = total_cost / valid_turnover if valid_turnover > 0 else 0

# ==========================================
# 区域 3: 测算结果输出 (Detailed Output)
# ==========================================
st.markdown("---")
st.header("2. 成本测算结果明细")

# 构建详细的数据表格
result_data = {
    "成本项目": [
        "GPS费用", "年检费", "主司机工资", "副司机工资", "保险费", 
        "车辆折旧费", # 虽然你没特意提，但作为固定成本必须列出来，否则总数对不上
        "油费 (满载/去程)", "油费 (空载/回程)", 
        "路桥费", "通讯费", "车辆大修", "车辆小修", "车辆轮胎", "车辆保养"
    ],
    "月度金额 (元)": [
        cost_gps, cost_check, salary_main, salary_vice, cost_insurance,
        cost_depreciation,
        cost_fuel_out, cost_fuel_in,
        cost_toll, cost_comm, cost_repair_major, cost_repair_minor, cost_tires, cost_maint
    ],
    "类别": [
        "固定成本", "固定成本", "固定成本", "固定成本", "固定成本", 
        "固定成本",
        "变动成本", "变动成本", 
        "变动成本", "变动成本", "变动成本", "变动成本", "变动成本", "变动成本"
    ]
}

df_res = pd.DataFrame(result_data)
# 格式化金额列，保留2位小数
df_res["月度金额 (元)"] = df_res["月度金额 (元)"].apply(lambda x: f"{x:,.2f}")

# 展示明细表
st.dataframe(df_res, use_container_width=True, hide_index=True)

# 展示核心汇总指标 (KPI Cards)
st.markdown("### 📊 核心指标汇总")
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("月固定成本", f"¥ {total_fixed:,.2f}")
with k2:
    st.metric("月变动成本", f"¥ {total_variable:,.2f}")
with k3:
    st.metric("月总成本", f"¥ {total_cost:,.2f}")
with k4:
    st.metric("单位成本 (元/吨公里)", f"¥ {unit_cost:.4f}", delta_color="inverse")
