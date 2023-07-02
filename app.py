import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report


df_agg = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:,:]
df_agg_sub = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                      'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                      'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']
df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'],format='%d/%m/%y %H:%M:%S.%f' )
#df_agg['Video publish time'] = df_agg['Video publish time'].apply(lambda x: datetime.strptime(x,'%d/%m/%y %H:%M:%S.%f'))
df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
df_agg['Engagement_ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] +df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
df_agg.sort_values('Video publish time', ascending = False, inplace = True)    


sidebar = st.sidebar.selectbox('select page ' , ('overview' , 'metrices' ,'video'))

if sidebar == 'overview' :
    st.header('OverView')
    pr = df_agg.profile_report()
    st_profile_report(pr)


if sidebar == 'metrices' :
    
    st.header('Total KPI ')
    l = ['Comments added', 'Shares', 'Dislikes', 'Likes','Views', 'Watch time (hours)', 'Subscribers' ]
    col1 , col2  = st.columns(2)
    cols = [col1 , col2 ]
    count = 0
    for i in l :
        with cols[count]:
            count +=1
            st.metric(i , round(sum(df_agg[i]) ,2) )
            if count >= 2 :
                count =0


    st.text("")
    st.text("")
    st.text("")

    st.header('metrices of cahnege per last 6 months')
    df_agg_metrics = df_agg[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months= 6)
    date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months= 12)
    metric_med_6 = df_agg_metrics[df_agg_metrics['Video publish time'] >= date_6mo ].median()
    st.dataframe(metric_med_6)
    metric_med_12 = df_agg_metrics[df_agg_metrics['Video publish time'] >= date_12mo ].median()
    #delta = metric_med_6['Views'] - metric_med_12['Views'] /  metric_med_12['Views']
    #st.metric('views change ' , metric_med_6['Views'] ,delta= delta)
    col6 , col7 , col8,col9,col10 = st.columns(5)
    cols = [col6 , col7 , col8,col9,col10 ]
    count = 0
    for i in metric_med_12.index :
        with cols[count]:
            count +=1
            #delta = (metric_med_6[i] - metric_med_12[i]) /  (metric_med_12[i])
            st.metric(i ,round(metric_med_6[i] ,2) ) # ,delta="{:.03f}".format(delta))
            if count >= 5 :
                count =0
    


if sidebar == 'video' :
    st.header("Individual Video Performance")
    videos = tuple(df_agg['Video title'])
    video_select = st.selectbox('Pick a Video:', videos)

    df_agg_metrics1 = df_agg[df_agg['Video title'] == video_select]
    df_agg_metrics = df_agg_metrics1[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months= 6)
    date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months= 12)
    metric_med_6 = df_agg_metrics[df_agg_metrics['Video publish time'] >= date_6mo ].median()
    metric_med_12 = df_agg_metrics[df_agg_metrics['Video publish time'] >= date_12mo ].median()
    
    st.text("")
    st.text("")
    st.text("")

    l = ['Comments added', 'Shares', 'Dislikes', 'Likes','Views', 'Watch time (hours)', 'Subscribers' ]
    col1 , col2 , col3,col4 = st.columns(4)
    cols = [col1 , col2 , col3,col4]
    count = 0
    for i in l :
        with cols[count]:
            count +=1
            st.metric(i , round(sum(df_agg_metrics1[i]) ,2) )
            if count >= 4 :
                count =0



    
    st.text("")
    st.text("")
    st.text("")
    col1 , col2 , col3,col4,col5 = st.columns(5)
    cols = [col1 , col2 , col3,col4,col5]
    count = 0
    for i in metric_med_12.index :
        with cols[count]:
            count +=1
            delta = metric_med_6[i] - metric_med_12[i] /  metric_med_12[i]
            st.metric(i , metric_med_6[i] ,delta= "{:.03f}".format(delta))
            if count >= 5 :
                count =0
    
    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code']#.apply(audience_simple)
    agg_sub_filtered.sort_values('Is Subscribed', inplace= True)   
    
    fig = px.bar(agg_sub_filtered, x ='Views', y='Is Subscribed', color ='Country', orientation ='h')
    #order axis 
    st.plotly_chart(fig)
    
