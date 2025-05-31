# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import uuid
from typing import Dict, List, Any

# 配置页面
st.set_page_config(
    page_title="Stock Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入你的MongoDB处理器和其他工具
try:
    from _mongo import MongoHandler
    from tz_api.api_news_fetcher import Summarizer
except ImportError:
    st.error("请确保已安装必要的依赖项和模块")
    st.stop()

# 样式和颜色定义
COLORS = {
    'positive': '#00d4aa',
    'negative': '#ff6b6b',
    'neutral': '#8884d8',
    'warning': '#ffa726'
}

# 辅助函数
def safe_get(data: Dict, key: str, default='N/A'):
    """安全获取字典值"""
    return data.get(key, default) if data else default

def safe_float(value, default=0.0):
    """安全转换为浮点数"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def format_market_cap(market_cap):
    """格式化市值"""
    if not market_cap or market_cap == 'N/A':
        return 'N/A'
    try:
        value = float(market_cap)
        if value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:,.0f}"
    except (ValueError, TypeError):
        return 'N/A'

def load_stock_data():
    """加载股票数据"""
    try:
        mongo_handler = MongoHandler()
        if not mongo_handler.is_connected():
            st.error("无法连接到数据库")
            return []
        
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz).date()
        five_days_ago = today - timedelta(days=5)
        
        # 获取最近5天的数据
        all_recent_data = mongo_handler.find_doc(
            'fundamentals_of_top_list_symbols',
            {'today_date': {'$gte': five_days_ago.strftime('%Y-%m-%d')}}
        )
        
        # 过滤和排序数据
        filtered_data = [x for x in all_recent_data if x.get('close_change_percentage') is not None]
        filtered_data.sort(key=lambda x: float(x['close_change_percentage']), reverse=True)
        
        return filtered_data
    except Exception as e:
        st.error(f"加载数据时出错: {str(e)}")
        return []

def create_price_chart(data):
    """创建价格图表"""
    day_low = safe_float(data.get('day_low'), 0)
    yesterday_close = safe_float(data.get('yesterday_close'), 0)
    day_close = safe_float(data.get('day_close'), 0)
    day_high = safe_float(data.get('day_high'), 0)
    market_open_high = safe_float(data.get('market_open_high'), 0)
    market_open_low = safe_float(data.get('market_open_low'), 0)
    
    fig = go.Figure()
    
    # 价格点
    x_positions = ['Yesterday Close', 'Day Low', 'Day High', 'Day Close']
    y_values = [yesterday_close, day_low, day_high, day_close]
    colors_list = [COLORS['neutral'], COLORS['negative'], COLORS['warning'], COLORS['positive']]
    
    # 添加价格线
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_values,
        mode='markers+lines',
        marker=dict(color=colors_list, size=12),
        line=dict(color=COLORS['neutral'], width=1),
        name='Price Movement',
        showlegend=False
    ))
    
    # 添加开盘高低点
    x_range = ['Yesterday Close', 'Day Close']
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[market_open_high, market_open_high],
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name=f'Market Open High ({market_open_high})'
    ))
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[market_open_low, market_open_low],
        mode='lines',
        line=dict(color='green', width=2, dash='dash'),
        name=f'Market Open Low ({market_open_low})'
    ))
    
    # 更新布局
    fig.update_layout(
        title=f"{safe_get(data, 'symbol')} Price Overview",
        xaxis_title='',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def create_cash_debt_chart(data):
    """创建现金债务图表"""
    sec_data = data.get('sec_filing_analysis', {})
    cash = safe_float(sec_data.get('Cash (USD)'))
    debt = safe_float(sec_data.get('Debt (USD)'))
    
    if cash is None and debt is None:
        fig = go.Figure()
        fig.add_annotation(
            text="No cash/debt data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title='Cash vs Debt Position',
            template='plotly_dark',
            height=350
        )
        return fig
    
    fig = go.Figure()
    
    if cash is not None:
        fig.add_trace(go.Bar(
            x=['Cash'],
            y=[cash/1000000],
            text=[f"${cash/1000000:.2f}M"],
            textposition='auto',
            marker_color=COLORS['positive'],
            name='Cash'
        ))
    
    if debt is not None:
        fig.add_trace(go.Bar(
            x=['Debt'],
            y=[debt/1000000],
            text=[f"${debt/1000000:.2f}M"],
            textposition='auto',
            marker_color=COLORS['negative'],
            name='Debt'
        ))
    
    fig.update_layout(
        title='Cash vs Debt Position (in millions USD)',
        yaxis_title='Amount (USD Millions)',
        template='plotly_dark',
        height=350
    )
    
    return fig

def display_stock_list():
    """显示股票列表页面"""
    st.title("📈 Stock Analytics Dashboard")
    
    # 加载数据
    with st.spinner("加载股票数据..."):
        stock_data = load_stock_data()
    
    if not stock_data:
        st.warning("暂无股票数据")
        return
    
    # 搜索和过滤
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 搜索股票代码或名称", placeholder="输入股票代码...")
    
    with col2:
        sectors = list(set([stock.get('sector', 'Unknown') for stock in stock_data]))
        selected_sector = st.selectbox("选择行业", ['全部'] + sectors)
    
    with col3:
        sort_by = st.selectbox("排序方式", ['涨跌幅', '价格', '市值'])
    
    # 过滤数据
    filtered_stocks = stock_data
    
    if search_term:
        filtered_stocks = [
            stock for stock in filtered_stocks 
            if search_term.lower() in stock.get('symbol', '').lower() 
            or search_term.lower() in stock.get('name', '').lower()
        ]
    
    if selected_sector != '全部':
        filtered_stocks = [
            stock for stock in filtered_stocks 
            if stock.get('sector') == selected_sector
        ]
    
    # 排序
    if sort_by == '价格':
        filtered_stocks.sort(key=lambda x: safe_float(x.get('day_close')), reverse=True)
    elif sort_by == '市值':
        filtered_stocks.sort(key=lambda x: safe_float(x.get('market_cap')), reverse=True)
    
    # 显示统计信息
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总股票数", len(filtered_stocks))
    
    with col2:
        positive_count = len([s for s in filtered_stocks if safe_float(s.get('close_change_percentage')) > 0])
        st.metric("上涨股票", positive_count, f"{positive_count/len(filtered_stocks)*100:.1f}%")
    
    with col3:
        negative_count = len([s for s in filtered_stocks if safe_float(s.get('close_change_percentage')) < 0])
        st.metric("下跌股票", negative_count, f"{negative_count/len(filtered_stocks)*100:.1f}%")
    
    with col4:
        avg_change = sum([safe_float(s.get('close_change_percentage')) for s in filtered_stocks]) / len(filtered_stocks)
        st.metric("平均涨跌幅", f"{avg_change:.2f}%")
    
    # 显示股票卡片
    st.markdown("---")
    st.subheader(f"股票列表 ({len(filtered_stocks)} 只)")
    
    # 每行显示3个股票卡片
    for i in range(0, len(filtered_stocks), 3):
        cols = st.columns(3)
        
        for j, col in enumerate(cols):
            if i + j < len(filtered_stocks):
                stock = filtered_stocks[i + j]
                display_stock_card(stock, col)

def display_stock_card(stock, col):
    """显示单个股票卡片"""
    change_percentage = safe_float(stock.get('close_change_percentage'), 0)
    change_color = COLORS['positive'] if change_percentage >= 0 else COLORS['negative']
    
    with col:
        # 创建可点击的容器
        container = st.container()
        
        with container:
            # 使用按钮来实现点击功能
            if st.button(
                f"📊 查看详情", 
                key=f"btn_{stock.get('symbol')}", 
                use_container_width=True
            ):
                st.session_state.selected_stock = stock.get('symbol')
                st.session_state.page = 'stock_detail'
                st.rerun()
            
            # 股票信息
            st.markdown(f"### {safe_get(stock, 'symbol')}")
            st.markdown(f"**{safe_get(stock, 'name')}**")
            st.markdown(f"**价格:** ${safe_get(stock, 'day_close')}")
            st.markdown(
                f"**涨跌幅:** <span style='color: {change_color}'>{change_percentage:.2f}%</span>", 
                unsafe_allow_html=True
            )
            st.markdown(f"**行业:** {safe_get(stock, 'sector')}")
            st.markdown(f"**Float Risk:** {safe_get(stock, 'float_risk')}")
            st.markdown(f"**日期:** {safe_get(stock, 'today_date')}")

def display_stock_detail():
    """显示股票详情页面"""
    if 'selected_stock' not in st.session_state:
        st.error("未选择股票")
        return
    
    # 返回按钮
    if st.button("← 返回股票列表"):
        st.session_state.page = 'stock_list'
        st.rerun()
    
    # 获取选中股票的数据
    stock_data = load_stock_data()
    selected_stock_data = None
    
    for stock in stock_data:
        if stock.get('symbol') == st.session_state.selected_stock:
            selected_stock_data = stock
            break
    
    if not selected_stock_data:
        st.error("找不到股票数据")
        return
    
    # 股票标题
    st.title(f"📈 {safe_get(selected_stock_data, 'symbol')} - {safe_get(selected_stock_data, 'name')}")
    
    # 主要指标
    col1, col2, col3, col4 = st.columns(4)
    
    change_percentage = safe_float(selected_stock_data.get('close_change_percentage'), 0)
    change_color = COLORS['positive'] if change_percentage >= 0 else COLORS['negative']
    
    with col1:
        st.metric("收盘价", f"${safe_get(selected_stock_data, 'day_close')}")
    
    with col2:
        st.metric(
            "涨跌幅", 
            f"{change_percentage:.2f}%",
            delta_color="normal" if change_percentage >= 0 else "inverse"
        )
    
    with col3:
        day_range = f"${safe_get(selected_stock_data, 'day_low')} - ${safe_get(selected_stock_data, 'day_high')}"
        st.metric("日内区间", day_range)
    
    with col4:
        market_cap_formatted = format_market_cap(selected_stock_data.get('market_cap'))
        st.metric("市值", market_cap_formatted)
    
    # 图表区域
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("价格走势")
        price_chart = create_price_chart(selected_stock_data)
        st.plotly_chart(price_chart, use_container_width=True)
    
    with col2:
        st.subheader("现金 vs 债务")
        cash_debt_chart = create_cash_debt_chart(selected_stock_data)
        st.plotly_chart(cash_debt_chart, use_container_width=True)
    
    # 详细信息区域
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 公司信息")
        company_info = {
            "股票代码": safe_get(selected_stock_data, 'symbol'),
            "公司名称": safe_get(selected_stock_data, 'name'),
            "行业": safe_get(selected_stock_data, 'sector'),
            "细分行业": safe_get(selected_stock_data, 'industry'),
            "国家": safe_get(selected_stock_data, 'countryDomicile'),
            "证券类型": safe_get(selected_stock_data, 'securityType'),
            "ISIN": safe_get(selected_stock_data, 'isin'),
            "Float": safe_get(selected_stock_data, 'float'),
            "Float Risk": safe_get(selected_stock_data, 'float_risk')
        }
        
        for key, value in company_info.items():
            st.text(f"{key}: {value}")
    
    with col2:
        st.subheader("📊 SEC 文件分析")
        sec_data = selected_stock_data.get('sec_filing_analysis', {})
        
        if sec_data:
            sec_info = {
                "现金 (USD)": safe_get(sec_data, 'Cash (USD)', 'N/A'),
                "债务 (USD)": safe_get(sec_data, 'Debt (USD)', 'N/A'),
                "现金/债务比率": safe_get(sec_data, 'Cash/Debt Ratio', 'N/A'),
                "ATM风险等级": safe_get(sec_data, 'ATM Risk Level', 'N/A'),
                "风险原因": safe_get(sec_data, 'Risk Reason', 'N/A'),
                "交易建议": safe_get(sec_data, 'Trading Recommendation', 'N/A'),
                "建议置信度": safe_get(sec_data, 'Recommendation Confidence', 'N/A'),
                "短期挤压风险": safe_get(sec_data, 'Short Squeeze Risk', 'N/A')
            }
            
            for key, value in sec_info.items():
                st.text(f"{key}: {value}")
            
            # 显示建议原因
            reasons = sec_data.get('Recommendation Reasons', [])
            if reasons:
                st.subheader("建议原因:")
                for reason in reasons:
                    st.write(f"• {reason}")
        else:
            st.write("暂无SEC分析数据")
    
    # 交易建议
    suggestion = safe_get(selected_stock_data, 'suggestion')
    if suggestion and suggestion != 'N/A':
        st.markdown("---")
        st.subheader("💡 交易建议")
        st.write(suggestion)
    
    # 新闻管理区域
    st.markdown("---")
    display_news_section(selected_stock_data)

def display_news_section(stock_data):
    """显示新闻管理区域"""
    st.subheader("📰 新闻管理")
    
    # 新闻输入
    with st.expander("添加新闻分析", expanded=False):
        password = st.text_input("密码", type="password")
        news_text = st.text_area("粘贴新闻内容", height=200)
        
        if st.button("提交新闻"):
            if password != "123456":
                st.error("密码错误")
            elif not news_text:
                st.error("请输入新闻内容")
            else:
                # 处理新闻提交
                success = submit_news(stock_data, news_text)
                if success:
                    st.success("新闻添加成功！")
                    st.rerun()
                else:
                    st.error("新闻添加失败")
    
    # 显示现有新闻
    raw_news = stock_data.get('raw_news', [])
    if raw_news:
        st.subheader("📄 已存储的新闻")
        
        for i, news in enumerate(raw_news):
            with st.expander(f"新闻 {i+1} - {news.get('timestamp', '')[:19]}"):
                st.write("**摘要:**")
                st.write(news.get('summary', ''))
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"查看完整内容 {i}", key=f"view_{i}"):
                        st.session_state[f'show_full_{i}'] = not st.session_state.get(f'show_full_{i}', False)
                
                with col2:
                    if st.button(f"删除", key=f"delete_{i}", type="secondary"):
                        if delete_news(stock_data, news.get('uuid')):
                            st.success("新闻删除成功")
                            st.rerun()
                        else:
                            st.error("删除失败")
                
                # 显示完整内容
                if st.session_state.get(f'show_full_{i}', False):
                    st.write("**完整内容:**")
                    st.write(news.get('text', ''))
    else:
        st.info("暂无新闻数据")

def submit_news(stock_data, news_text):
    """提交新闻"""
    try:
        mongo = MongoHandler()
        if not mongo.is_connected():
            return False
        
        # 获取GPT摘要
        gpt_summarizer = Summarizer()
        summary = gpt_summarizer.summarize(news_text)
        
        # 创建新闻条目
        news_entry = {
            "uuid": str(uuid.uuid4()),
            "text": news_text,
            "summary": summary,
            "timestamp": datetime.now(ZoneInfo("America/New_York")).isoformat()
        }
        
        # 更新数据库
        collection_name = "fundamentals_of_top_list_symbols"
        symbol = stock_data.get('symbol')
        date = stock_data.get('today_date')
        query = {"symbol": symbol, "today_date": date}
        
        existing_doc = mongo.find_one(collection_name, query)
        raw_news_list = existing_doc.get("raw_news", []) if existing_doc else []
        raw_news_list.append(news_entry)
        
        # 生成新建议
        existing_suggestion = existing_doc.get("suggestion", "None") if existing_doc else "None"
        prompt_for_suggestion = f"""
        新的新闻 (New News):
        {summary}

        原有的总结 (Original Summary):
        {existing_suggestion}

        请为这则新闻提供建议 (Please provide suggestions for this input):
        """
        new_suggestion = gpt_summarizer.suggestion(prompt_for_suggestion)
        
        # 更新文档
        update_data = {
            "raw_news": raw_news_list,
            "suggestion": new_suggestion
        }
        
        result = mongo.upsert_doc(collection_name, query, update_data)
        return result is not None
        
    except Exception as e:
        st.error(f"提交新闻时出错: {str(e)}")
        return False

def delete_news(stock_data, news_uuid):
    """删除新闻"""
    try:
        mongo = MongoHandler()
        if not mongo.is_connected():
            return False
        
        collection_name = "fundamentals_of_top_list_symbols"
        symbol = stock_data.get('symbol')
        date = stock_data.get('today_date')
        query = {"symbol": symbol, "today_date": date}
        
        doc = mongo.find_one(collection_name, query)
        if not doc or 'raw_news' not in doc:
            return False
        
        # 过滤掉要删除的新闻
        updated_news = [n for n in doc['raw_news'] if n.get("uuid") != news_uuid]
        
        result = mongo.update_one(collection_name, query, {"raw_news": updated_news})
        return result and result.get('modified_count', 0) > 0
        
    except Exception as e:
        st.error(f"删除新闻时出错: {str(e)}")
        return False

def main():
    """主函数"""
    try:
        # 初始化session state
        if 'page' not in st.session_state:
            st.session_state.page = 'stock_list'
        
        # 侧边栏导航
        with st.sidebar:
            st.title("📊 导航")
            
            if st.button("📈 股票列表", use_container_width=True):
                st.session_state.page = 'stock_list'
                st.rerun()
            
            if st.button("📋 策略分析", use_container_width=True):
                st.session_state.page = 'strategy'
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 Dashboard Info")
            st.markdown("实时股票分析和交易建议")
            st.markdown("数据更新时间: 每5分钟")
        
        # 路由到相应页面
        if st.session_state.page == 'stock_list':
            display_stock_list()
        elif st.session_state.page == 'stock_detail':
            display_stock_detail()
        elif st.session_state.page == 'strategy':
            st.title("📋 策略分析")
            st.info("策略分析功能正在开发中...")
    
    except Exception as e:
        st.error(f"应用程序运行出错: {str(e)}")

if __name__ == "__main__":
    main()