import streamlit as st
import pandas as pd
from pickle import load as pickle_load

# Set page config
st.set_page_config(layout="wide", page_title="Fon Analysis")

# Custom CSS to enhance design
# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 20px;
    }
    .stSidebar {
        background-color: #282828;
        color: #ffffff;
    }
    .title {
        font-size: 2.5em;
        font-weight: bold;
        color: #2e86c1;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 1.5em;
        color: #2874a6;
        margin-bottom: 15px;
    }
    .box {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    .ag-theme-streamlit {
        --ag-header-background-color: #2e86c1;
        --ag-header-foreground-color: #ffffff;
        --ag-odd-row-background-color: #f9f9f9;
        --ag-row-hover-color: #cfe2f3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def read_stock_clode_data(file_path):
    output_data= pd.read_csv(file_path)
    return output_data


@st.cache_data
def read_data(file_path):
    with open(file_path, 'rb') as handle:
        output_data = pickle_load(handle)
    return output_data

def calculate_percentage_change(a, b):
    if a is None or b is None:
        return None
    try:
        return ((b - a) / a) * 100
    except ZeroDivisionError:
        return None  
    
def highlight_max(s):
    is_max = s == s.max()
    return ['background-color: lightgreen' if v else '' for v in is_max]

def highlight_degisim(val):
    color = 'green' if val > 0 else 'white'
    return f'background-color: {color}'

def highlight_cells(val):
    if pd.isna(val):
        color = 'white'
    elif val > 10:
        color = 'green'
    elif val > 0:
        color = 'lightgreen'
    else:
        color = 'white'
    return f'background-color: {color}'


# Load data
analysis_result = read_data("analysis_data.pickle")
df = pd.DataFrame(analysis_result["TUM_FONLAR"])
stock_close_data= read_stock_clode_data("stock_close_data.csv")

# Sidebar filters
st.sidebar.title("Filters")
selected_fon_adi = st.sidebar.selectbox("Select Fon Adi", options=sorted(df['fon_adi'].unique()))
selected_period = st.sidebar.selectbox("Select Period", options=sorted(df[df["fon_adi"]==selected_fon_adi]['period'].unique(), reverse=True))

st.sidebar.dataframe(df[["fon_adi","company_name"]].drop_duplicates("fon_adi").sort_values(by='fon_adi').set_index('fon_adi'))


# Apply filters
filtered_df = df[(df['fon_adi']==selected_fon_adi) & (df['period']==selected_period)]

last_period =sorted(df[(df['fon_adi']==selected_fon_adi)]['period'].unique(), reverse=True)[0]
previous_period = sorted(df[(df['fon_adi']==selected_fon_adi)]['period'].unique(), reverse=True)[1]

prev_data = df[(df['fon_adi']==selected_fon_adi) & (df['period']==previous_period)][["hisse_kodu","yuzdelik_deger"]].rename(columns={"yuzdelik_deger":"yuzdelik_deger_eski"})
last_data = df[(df['fon_adi']==selected_fon_adi) & (df['period']==last_period)][["hisse_kodu","yuzdelik_deger","alis_tarihi"]].rename(columns={"yuzdelik_deger":"yuzdelik_deger_yeni"})


prev_last_diff_data = pd.merge(prev_data,last_data, on = ["hisse_kodu"],how ='outer').set_index("hisse_kodu")


df_new = prev_last_diff_data[prev_last_diff_data.isna().any(axis=1)]
# df_new["alis_satis_tarihi"] = df_new['alis_tarihi'].combine_first(df_new['satis_tarihi'])
df_new = pd.merge(df_new,stock_close_data.rename(columns={'Date':'alis_tarihi','Close':'alis_fiyat'}),on=["hisse_kodu",'alis_tarihi'],how="left")

df_new = pd.merge(df_new,stock_close_data.rename(columns={'Close':'son_fiyat'}), on=["hisse_kodu"],how="left")
df_new['Date'] = pd.to_datetime(df_new['Date'], errors='coerce')
df_new = df_new[df_new["Date"]==df_new['Date'].max()].drop(columns="Date").reset_index(drop=True)
df_new["degisim"] =df_new.apply(lambda x: calculate_percentage_change(x['alis_fiyat'], x['son_fiyat']), axis=1)




fon_adim = filtered_df["company_name"].values[0]
filtered_df = filtered_df.drop(columns = 'company_name').reset_index(drop=True)

# Main title
st.markdown('<div class="title">Fon Analysis Dashboard</div>', unsafe_allow_html=True)


st.write(f"{fon_adim}")

st.write(f"https://www.kap.org.tr/tr/Bildirim/{filtered_df['rapor_index'].values[0]}")

# Display filtered DataFrame
st.markdown('<div class="subtitle">Filtered DataFrame</div>', unsafe_allow_html=True)
st.write("Use the filters on the sidebar to select Fon Adi and Period:")
st.dataframe(filtered_df.style.set_properties(**{'background-color': 'white', 'color': 'black'}),width=1200)

# Newly Added vs Removed Stocks
st.markdown('<div class="subtitle">New Added vs Removed Stocks in the Last Month</div>', unsafe_allow_html=True)
st.dataframe(df_new.style.applymap(highlight_degisim, subset=['degisim']),width=1200)

# Prev vs Current Fon Stocks
st.markdown('<div class="subtitle">Prev vs Current Fon Stocks</div>', unsafe_allow_html=True)
st.dataframe(prev_last_diff_data.drop(columns="alis_tarihi").style.apply(highlight_max, subset=['yuzdelik_deger_eski', 'yuzdelik_deger_yeni'], axis=1),width=1200)

# Analysis Section

st.markdown('<div class="subtitle">Analysis</div>', unsafe_allow_html=True)

# Analysis layout
col1, col2 = st.columns(2)

# row_spacer1, col1, row_spacer2, col2,row_spacer3 = st.columns((1,4,1, 4, 1))

with col1:
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.write("### Most Chosen Stocks Over Fons")
    most_chosen_stocks = df['hisse_kodu'].value_counts().reset_index()
    most_chosen_stocks.columns = ['hisse_kodu', 'count']
    st.dataframe(most_chosen_stocks.style.set_properties(**{'background-color': 'white', 'color': 'black'}),width=1200)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="box">', unsafe_allow_html=True)
    last_period = df['period'].max()
    st.write(f"### Most Chosen Stocks in the Last Period ({last_period})")
    last_period_stocks = df[df['period']==selected_period]['hisse_kodu'].value_counts().reset_index()
    last_period_stocks.columns = ['hisse_kodu', 'count']
    st.dataframe(last_period_stocks.style.set_properties(**{'background-color': 'white', 'color': 'black'}),width=1200)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="box">', unsafe_allow_html=True)
st.write("### Stock Distribution Over Periods (Selected Fon)")
stock_period_distribution = df[df['fon_adi'] == selected_fon_adi].groupby(['hisse_kodu', 'period']).size().unstack(fill_value=0)
st.dataframe(stock_period_distribution.style.applymap(highlight_cells),width=1200)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="box">', unsafe_allow_html=True)
st.write("### Stock Distribution Over Periods")
stock_period_distribution = df.groupby(['hisse_kodu', 'period']).size().unstack(fill_value=0)
st.dataframe(stock_period_distribution.style.applymap(highlight_cells),width=1200)
st.markdown('</div>', unsafe_allow_html=True)
