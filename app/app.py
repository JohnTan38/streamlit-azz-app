import streamlit as st
import pandas as pd
import numpy as np
import math,re
from datetime import datetime
#import win32com.client
import glob, os, openpyxl, re
#import pythoncom
import warnings
warnings.filterwarnings("ignore")

import datetime as datetime
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config('PSA Rebates', page_icon="🏛️", layout='wide')
def title(url):
     st.markdown(f'<p style="color:#2f0d86;font-size:22px;border-radius:2%;"><br><br><br>{url}</p>', unsafe_allow_html=True)
def title_main(url):
     st.markdown(f'<h1 style="color:#230c6e;font-size:42px;border-radius:2%;"><br>{url}</h1>', unsafe_allow_html=True)

def success_df(html_str):
    html_str = f"""
        <p style='background-color:#baffc9;
        color: #313131;
        font-size: 15px;
        border-radius:5px;
        padding-left: 12px;
        padding-top: 10px;
        padding-bottom: 12px;
        line-height: 18px;
        border-color: #03396c;
        text-align: left;'>
        {html_str}</style>
        <br></p>"""
    st.markdown(html_str, unsafe_allow_html=True)

title_main('PSA Rebates Data Visualization')
st.sidebar.header("Line graph")
lst_num_week = st.sidebar.multiselect('Select number of weeks to plot', [5,6,7,8,9,10], placeholder='Choose 1', 
                          max_selections=2)
if st.sidebar.button('Confirm weeks'):
    if lst_num_week is not None:
        st.sidebar.write(f'Selected weeks: {lst_num_week[0]}')
        num_week = lst_num_week[0]
    else:
        st.sidebar.write('please select number of weeks')

def user_email(usr_name):
    usr_email = usr_name[0] + '@sh-cogent.com.sg'
    return usr_email

def merge_cod_atd(df_week, df_transport):
    # Merge the dataframes on 'ContainerNumber' and 'EventTime'
    df_merged = pd.merge(df_week, df_transport, on=['ContainerNumber', 'CarrierName'], how='left')
        
    df_merged['COD_ATD'] = df_merged['COD_ATD'].fillna('-') # Fill NaN values in 'COD_ATD' with '-'
  
    df_week_appended = df_merged[['ContainerNumber', 'CarrierName', 'Size Type', 'EventTime_x', 'COD_ATD']] # Select the required columns
    df_week_appended = df_week_appended.rename(columns={'Size Type': 'Size', 'EventTime_x': 'EventTime'})
    return df_week_appended

dataUpload = st.file_uploader("Upload (1) Week.xlsx (2) Transport_KPI.xlsx files", type="xlsx", accept_multiple_files=True)
if dataUpload is None:
        st.text("Please upload a file")
elif dataUpload is not None:
        for file in dataUpload:
            if 'Week_' in file.name:
                week_number = file.name.split('_')[1].split('.')[0] #get week number
                df_week_arrive = pd.read_excel(file, sheet_name='Arrival', engine='openpyxl') #'Week_36_1.xlsx'
                df_week_arrive = df_week_arrive[['ContainerNumber', 'CarrierName', 'Size Type', 'EventTime']]
                df_week_exit = pd.read_excel(file, sheet_name='Exit', engine='openpyxl') #'Week_36_1.xlsx'
                df_week_exit = df_week_exit[['ContainerNumber', 'CarrierName', 'Size Type', 'EventTime']]
                #df_week_2_arrive = pd.read_excel(path_transport+ 'Week_36_2.xlsx', sheet_name='Arrival', engine='openpyxl')
                #df_week_2_arrive = df_week_2_arrive[['ContainerNumber', 'CarrierName', 'Size Type', 'EventTime']]
                #df_week_2_exit = pd.read_excel(path_transport+ 'Week_36_2.xlsx', sheet_name='Exit', engine='openpyxl')
                #df_week_2_exit = df_week_2_exit[['ContainerNumber', 'CarrierName', 'Size Type', 'EventTime']]

                df_week = pd.concat([df_week_arrive, df_week_exit])

                # Convert 'EventTime' to 24-hour format
                df_week['EventTime'] = pd.to_datetime(df_week['EventTime']).dt.strftime('%Y-%m-%d %H:%M:%S')
                st.write(f"Week {week_number} data processed successfully")
            elif 'Transport_KPI_Monitoring' in file.name:
                week_number = file.name.split('_')[3].split('.')[0]
                df_transport = pd.read_excel(file, sheet_name='Week '+week_number, parse_dates=['EventTime'], engine='openpyxl')
                df_transport = df_transport[['ContainerNumber', 'CarrierName', 'EventTime', 'COD_ATD']]
                df_transport['EventTime'] = df_transport['EventTime'].str.replace('am', 'AM').str.replace('pm', 'PM')
                try:
                    df_transport['EventTime'] = pd.to_datetime(df_transport['EventTime'], format='%d/%m/%Y %I:%M:%S %p', dayfirst=True)#.dt.strftime()
                except Exception as e:
                    print(e)
                
                
                df_week_appended = merge_cod_atd(df_week, df_transport)
                #df_week_appended['EventTime'] = pd.to_datetime(df_week_appended['EventTime'], format='%Y-%m-%d %H:%M:%S')
                def remove_invalid_rows(df):
                    # Remove rows where 'COD_ATD' is '-'
                    df_cleaned = df[df['COD_ATD'] != '-']
                    return df_cleaned

                df_week_appended= remove_invalid_rows(df_week_appended)    

                #2
                def format_datetime_columns(df, columns, date_format):
                    for column in columns:
                            try:
                                df[column] = pd.to_datetime(df[column], format=date_format)
                            except ValueError:
                                #print(f"Invalid date format for column: {column}")
                                pass
                    return df

                def calculate_time_difference(df):                    
                        #df['Time_Difference'] = None # Calculate Time_Difference based on conditions
                        df['Time_Difference'] = (df['COD_ATD'] - df['EventTime']).dt.total_seconds() / 60
                        #df.loc[df['Arrive_Time'].isna(), 'Time_Difference'] = (df['Exit_Time'] - df['Complete_Discharge_Time']).dt.total_seconds() / 60
   
                        #df['PSA_Rebate'] = np.nan # Initialize a new column 'PSA_Rebate' with NaN values

                        # Assign 'PSA_Rebate' based on 'Time_Difference'
                        df.loc[df['Time_Difference'] < 24*60, 'PSA_Rebate'] = 1
                        df.loc[(df['Time_Difference'] >= 24*60) & (df['Time_Difference'] < 48*60), 'PSA_Rebate'] = 2
                        return df

                df_week_appended = format_datetime_columns(df_week_appended, ['COD_ATD'], '%Y-%m-%d %H:%M:%S') # Convert 'EventTime' and 'COD_ATD' columns to datetime format
                df_week_appended = format_datetime_columns(df_week_appended, ['EventTime'], '%Y-%d-%m %H:%M:%S')
                df_calculate_time_difference = calculate_time_difference(df_week_appended)
                if (df_calculate_time_difference['Time_Difference'].values< 0).any():
                    df_calculate_time_difference['Time_Difference'] = df_calculate_time_difference['Time_Difference'].abs()


                df_public_holidays = pd.read_excel("https://raw.githubusercontent.com/JohnTan38/Project-Income/main/public_holidays.xlsx", sheet_name='public_holidays', 
                                                engine='openpyxl')
                public_holidays = df_public_holidays['public_holidays'].tolist() # Define the public holidays in Singapore
                def extract_numeric(df):
                    df['Size'] = df['Size'].str.extract('(\\d+)', expand=False)  # Use regular expression to extract numeric part of 'Size' column
                    return df
                
                def add_offpeak_columns(df_rebate):
                    df_rebate['EventTime'] = pd.to_datetime(df_rebate['EventTime'], format='%Y-%m-%d %H:%M:%S') # Convert the 'Event_Time' column to datetime

                    # Initialize the 'Offpeak_24' and 'Offpeak_48' columns with 0
                    df_rebate['Offpeak_24'] = 0
                    df_rebate['Offpeak_48'] = 0
                    df_rebate['peak_24'] = 0
                    df_rebate['peak_48'] = 0

                    # Iterate over the rows of the DataFrame
                    for i, row in df_rebate.iterrows():
                        # Check if the event time is a Sunday, a public holiday, or between 21:00 and 04:59
                        if row['EventTime'].weekday() == 6 or row['EventTime'].strftime('%Y-%m-%d') in public_holidays or (row['EventTime'].hour >= 21 or row['EventTime'].hour < 5):
                            # If 'PSA_Rebate' is 1, set 'Offpeak_24' to 1 and others to 0
                            if row['PSA_Rebate'] == 1.0:
                                    df_rebate.at[i, 'Offpeak_24'] = 1
                                    df_rebate.at[i, 'Offpeak_48'] = 0
                                    df_rebate.at[i, 'peak_24'] = 0
                                    df_rebate.at[i, 'peak_48'] = 0
                            # If 'PSA_Rebate' is 2, set 'Offpeak_48' to 1 and others to 0
                            elif row['PSA_Rebate'] == 2.0:
                                    df_rebate.at[i, 'Offpeak_48'] = 1
                                    df_rebate.at[i, 'Offpeak_24'] = 0
                                    df_rebate.at[i, 'peak_24'] = 0
                                    df_rebate.at[i, 'peak_48'] = 0
    
                    for i, row in df_rebate.iterrows():
                        # Check if the event time is not Sunday, not public holiday, or between 07:00 and 22:59
                        if (row['EventTime'].weekday() != 6 and row['EventTime'].strftime('%Y-%m-%d') not in public_holidays) and (row['EventTime'].hour >= 7 or row['EventTime'].hour < 23):
                            # If 'PSA_Rebate' is 1, set 'peak_24' to 1
                            if row['PSA_Rebate'] == 1.0:
                                    df_rebate.at[i, 'peak_24'] = 1
                                    df_rebate.at[i, 'peak_48'] = 0
                                    df_rebate.at[i, 'Offpeak_24'] = 0
                                    df_rebate.at[i, 'Offpeak_48'] = 0
                            # If 'PSA_Rebate' is 2, set 'Offpeak_48' to 1
                            elif row['PSA_Rebate'] == 2.0:
                                    df_rebate.at[i, 'peak_48'] = 1
                                    df_rebate.at[i, 'peak_24'] = 0
                                    df_rebate.at[i, 'Offpeak_24'] = 0
                                    df_rebate.at[i, 'Offpeak_48'] = 0
            
                    extract_numeric(df_rebate)
                    return df_rebate
                

                psa_offpeak_peak_rates = pd.read_csv(r"https://raw.githubusercontent.com/JohnTan38/Project-Income/main/psa_rebate.csv", index_col=0)
                #offpeak rebate
                offpeak_20_24 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('offpeak_24')] #35
                offpeak_20_48 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('offpeak_48')] #15
                offpeak_40_24 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('offpeak_24')] #52.5
                offpeak_40_48 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('offpeak_48')] #22.5
                #peak rebate
                peak_20_24 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('peak_24')] #25
                peak_20_48 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('peak_48')] #10
                peak_40_24 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('peak_24')] #37.5
                peak_40_48 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('peak_48')] #15

                def calculate_rebate(df):
                # Define a function to calculate reate based on the conditions
                    def rebate(row):
                        #if row['Offpeak_24'] == 1:
                        if row['Size'] == '20':
                                return offpeak_20_24 if row['Offpeak_24'] == 1 else offpeak_20_48 if row['Offpeak_48'] == 1 else 0
                        elif row['Size'] == '40':
                                return offpeak_40_24 if row['Offpeak_24'] == 1 else offpeak_40_48 if row['Offpeak_48'] == 1 else 0
            
                        #elif row['Nonpeak'] == 'No':
                        if row['Size'] == '20':
                                return peak_20_24 if row['peak_24'] == 1 else peak_20_48 if row['peak_48'] == 1 else 0
                        elif row['Size'] == '40':
                                return peak_40_24 if row['peak_24'] == 1 else peak_40_48 if row['peak_48'] == 1 else 0
                        #else:
                        return 0

                    # Apply the function to each row in the DataFrame to calculate the rebate
                    df['Rebate'] = df.apply(rebate, axis=1)
                    return df
                df_calculate_rebate = calculate_rebate(add_offpeak_columns(calculate_time_difference(df_week_appended)))

                def count_occurrences(df_rebate):
                # Initialize a new DataFrame with the desired index and columns
                    df_count = pd.DataFrame(index=['20', '40'], columns=['Offpeak_24', 'Offpeak_48', 'peak_24', 'peak_48'])

                    # Count the occurrences and fill the new DataFrame
                    for size in ['20', '40']:
                        for offpeak in ['Offpeak_24', 'Offpeak_48', 'peak_24', 'peak_48']:
                            df_count.at[size, offpeak] = df_rebate[(df_rebate['Size'] == size) & (df_rebate[offpeak] == 1)].shape[0]
                        #for peak in ['peak_24', 'peak_48']:
                            #df_count.at[size, peak] = df_rebate[(df_rebate['Size'] == size) & (df_rebate[peak] == 1)].shape[0]    

                    return df_count

                def style_dataframe(df):
                    return df.style.set_table_styles(
                        [{
                        'selector': 'th',
                        'props': [
                            ('background-color', 'navy'),
                            ('color', 'antiquewhite'),
                            ('font-family', 'Arial, sans-serif'),
                            ('font-size', '12px') ##4CAF50
                                ]
                        }, 
                    {
                        'selector': 'td, th',
                        'props': [
                            ('border', '1px solid paleturquoise')
                                ]
                    }]
                    )
                def display_dataframe(df):
                    styled_df = style_dataframe(df)
                    st.write(styled_df.to_html(), unsafe_allow_html=True)

                def format_dataframe_2_decimal(df):
                    # Apply formatting to all columns in DataFrame
                    formatted_df = df.round(2)
                    # Set display option to show only two decimals
                    pd.options.display.float_format = '{:.2f}'.format
                    return formatted_df           
            
                offpeak_rebate_count = count_occurrences(df_calculate_rebate)
                offpeak_rebate_count.dropna(subset=['Offpeak_24', 'Offpeak_48', 'peak_24', 'peak_48'], inplace=True)
                st.subheader("Count of containers")
                display_dataframe(offpeak_rebate_count)
                # Define the function to multiply rates and sum across columns
                def multiply_and_sum(df):
                    result_df = pd.DataFrame(index=['20', '40'], columns=['Offpeak_and_peak_24', 'Offpeak_and_peak_48'])
    
                    result_df.loc['20', 'Offpeak_and_peak_24'] = (df.loc['20', 'Offpeak_24'] * offpeak_20_24) + (df.loc['20', 'peak_24'] * peak_20_24)
                    result_df.loc['20', 'Offpeak_and_peak_48'] = (df.loc['20', 'Offpeak_48'] * offpeak_20_48) + (df.loc['20', 'peak_48'] * peak_20_48)
    
                    result_df.loc['40', 'Offpeak_and_peak_24'] = (df.loc['40', 'Offpeak_24'] * offpeak_40_24) + (df.loc['40', 'peak_24'] * peak_40_24)
                    result_df.loc['40', 'Offpeak_and_peak_48'] = (df.loc['40', 'Offpeak_48'] * offpeak_40_48) + (df.loc['40', 'peak_48'] * peak_40_48)
    
                    return result_df

                # Apply the function and print the result
                def max_value_of_df(df):
                    return (df.max().max()) - 1
                

                offpeak_peak_df = multiply_and_sum(offpeak_rebate_count) # Apply the function and display the result
                offpeak_peak_df = format_dataframe_2_decimal(offpeak_peak_df)
                highest_rebate = max_value_of_df(offpeak_peak_df)
                offpeak_peak_df_color = offpeak_peak_df.style.map(lambda x: f"background-color: {'palegreen' if x>highest_rebate else 'lemonchiffon'}", subset=['Offpeak_and_peak_24','Offpeak_and_peak_48'])
                st.subheader("Rebates")
                st.dataframe(offpeak_peak_df_color)
                #display_dataframe(offpeak_peak_df_color)

                df_total_offpeak_peak = pd.DataFrame(index=['20','40'], columns=['total_offpeak_peak_rebate'])
                df_total_offpeak_peak['total_offpeak_peak_rebate'] = offpeak_peak_df.sum(axis=1).round(2)
                st.header('Total $Rebates 20ft 40ft')
                display_dataframe(df_total_offpeak_peak)

                import math
                def compute_psa_lolo(df_psa):
                    df_psa['PSALOLO'] = df_psa['PSALOLO'].fillna(0)
                    df_psa['PSALOLO'] = df_psa['PSALOLO'].astype(float)
                    df_psa['Size'] = df_psa['Size'].str.extract('(\d+)').astype(int)
                
                    psa_lolo_20 = df_psa[df_psa['Size'] == 20]['PSALOLO'].sum() # Sum all rows of 'PSALOLO' where 'Size' == 20
                    psa_lolo_40 = df_psa[df_psa['Size'] == 40]['PSALOLO'].sum() # Sum all rows of 'PSALOLO' where 'Size' == 40
                    # Create a new DataFrame with the results
                    df_psa_lolo = pd.DataFrame({'PSALOLO': [psa_lolo_20, psa_lolo_40]}, index=[20, 40]) # Create new DataFrame with results
                    return df_psa_lolo
                 
                df_overall_rebate_efficiency = pd.read_excel(r'https://raw.githubusercontent.com/JohnTan38/Project-Income/main/Overall_Rebate_Efficiency.xlsx', 
                                            sheet_name='OverallRebateEfficiency', engine='openpyxl')
                df_psa_lolo = pd.read_excel(r'https://raw.githubusercontent.com/JohnTan38/Project-Income/main/Overall_Rebate_Efficiency.xlsx', 
                                    sheet_name='PSA_LOLO', engine='openpyxl')
                # Set the 'Unnamed: 0' column as the index
                df_psa_lolo.set_index('Unnamed: 0', inplace=True)
                df_overall_rebate_efficiency.set_index('Week', inplace=True)
                #df_psa_lolo = compute_psa_lolo(df_week_appended)
                psa_lolo_20 = df_psa_lolo['PSALOLO'][20]
                psa_lolo_40 = df_psa_lolo['PSALOLO'][40]
                #sum across cols
                def sum_cols(df, col_sum):
                        df[col_sum] = df.sum(axis=1)
                        return df
            
                #df_rebate_total=sum_cols(df_offpeak_rebate_sums, 'sum_offpeak_rebate')
                rebate_efficiency_20 = (df_total_offpeak_peak['total_offpeak_peak_rebate']['20'] /psa_lolo_20) /0.5932
                rebate_efficiency_40 = (df_total_offpeak_peak['total_offpeak_peak_rebate']['40'] /psa_lolo_40) /0.5932
                #overall_rebate_efficiency = math.ceil(((rebate_efficiency_20+rebate_efficiency_40)/2)*100) /100 #round 2 decimals
                overall_rebate_efficiency = round(((rebate_efficiency_20+rebate_efficiency_40)/2),4) #4 decimals

                def add_column(df,new_week):
                        last_column = df.columns[-1]
                        last_week_number = int(last_column.split('_')[-1]) #get week number of last col
                        new_column = 'Week_'+ str(last_week_number+1)
                        df[new_column] = new_week
                        return df
                
                import datetime
                today_date = datetime.datetime.today().strftime('%Y-%m-%d') #format as str
                date = datetime.datetime.strptime(today_date, '%Y-%m-%d')
                week_num = date.isocalendar()[1] #get week num of current date
                week_num=37 #development

                def get_week_number(df_rebate_efficiency):
                        last_week_label = df_rebate_efficiency['Week'].iloc[-1] #get the last week label
                        week_number = int(last_week_label.split('_')[-1])
                        return week_number
                
                if week_num != get_week_number(df_overall_rebate_efficiency.reset_index()):
                    df_overall_rebate_efficiency_new = add_column(df_overall_rebate_efficiency.T, overall_rebate_efficiency)
                else:
                    df_overall_rebate_efficiency_new = df_overall_rebate_efficiency.T

                # Transpose the DataFrame to have weeks as rows
                df_overall_rebate_efficiency_new = df_overall_rebate_efficiency_new.T
                df_overall_rebate_efficiency_new.columns = ['Efficiency']
                df_overall_rebate_efficiency_new.index.name = 'Week'

                def plot_efficiency(df_efficiency,num_weeks):
    
                        df_to_plot = df_efficiency.tail(num_weeks) # Select the number of weeks to plot
        
                        fig=plt.figure(figsize=(10, 5)) # Plot the line chart
                        plt.plot(df_to_plot.index, (df_to_plot['Efficiency']*100).round(2), marker='o')
                        for x,y in zip(df_to_plot.index, (df_to_plot['Efficiency']*100).round(2)):
                                plt.text(x,y, f'{y:.2f}%', ha='center', va='bottom')
    
                        plt.ylim(0,100)
                        plt.xlabel('Week Number')
                        plt.ylabel('Efficiency (%)')
                        plt.title('PSA Loaded Rebates Efficiency') # Set the labels and title    
                        #plt.show() # Show the plot
                        st.pyplot(fig) #streamlit

                #num_week = int(input("Enter the number of weeks to plot: ")) # User input for the number of weeks to plot
                plot_efficiency(df_overall_rebate_efficiency_new,lst_num_week[0]) # Call the function with the user input

                def append_dollar(df):
                        # Iterate over each col in df
                        for col in df.columns:
                            # Convert the col to string, Add '$' to the beginning of each col
                            df[col] = '$' + df[col].astype(str) 
                            return df

                def create_offpeak_peak_count(df):
                    # Calculate the sums for 'Offpeak_and_peak_24' and 'Offpeak_and_peak_48'
                    offpeak_and_peak_24 = [df.loc['20', 'Offpeak_24'] + df.loc['20', 'peak_24'], df.loc['40', 'Offpeak_24'] + df.loc['40', 'peak_24']]
                    offpeak_and_peak_48 = [df.loc['20', 'Offpeak_48'] + df.loc['20', 'peak_48'], df.loc['40', 'Offpeak_48'] + df.loc['40', 'peak_48']]
    
                    # Create the new DataFrame
                    df_offpeak_peak_count = pd.DataFrame({
                        'Offpeak_and_peak_24': offpeak_and_peak_24,
                        'Offpeak_and_peak_48': offpeak_and_peak_48
                        }, index=['20', '40'])
    
                    return df_offpeak_peak_count
                
                def plot_clustered_bar_charts(df_count, df_rebate):
                        # Set the color palette as gradient from light blue to dark blue
                        sns.set_palette(sns.color_palette("Blues", len(df_count.columns)))
    
                        # Define the number of bars per group
                        n_bars = len(df_count.columns)
    
                        # Define the positions of the bars
                        bar_width = 0.35
                        index = np.arange(len(df_count.index))
    
                        # Create the figure and axis
                        fig, ax = plt.subplots()
    
                        # Plot each bar group
                        for i, column in enumerate(df_count.columns):
                            bar_positions = index + i * bar_width
                            bars = ax.bar(bar_positions, df_count[column], bar_width, label=column, color=plt.cm.Blues(0.5+ i / 2*n_bars))
        
                            # Annotate each bar with the corresponding rebate value
                            for j, bar in enumerate(bars):
                                height = bar.get_height()
                                ax.annotate(f'{df_rebate[column][j]}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')
    

                        dynamic_max_value = max(int(df_count.max().max()), 450)
                        plt.ylim(0, dynamic_max_value + dynamic_max_value*0.15) # Set the dynamic y-axis limit
                        # Set the labels and title
                        ax.set_xlabel('Container size')
                        ax.set_ylabel('Count')
                        ax.set_title('Bar Charts with Rebate Annotations')
                        ax.set_xticks(index + bar_width / 2)
                        ax.set_xticklabels(df_count.index)
                        ax.legend()
                        #plt.show() # Show the plot
                        st.pyplot(fig,ax)

                #df_offpeak_rebate_sums_dollar = append_dollar(offpeak_peak_df)
                #call the function
                plot_clustered_bar_charts(create_offpeak_peak_count(offpeak_rebate_count), offpeak_peak_df) 
                

footer_html = """
    <div class="footer">
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f0f2f6;
            padding: 10px 20px;
            text-align: center;
        }
        .footer a {
            color: #4a4a4a;
            text-decoration: none;
        }
        .footer a:hover {
            color: #3d3d3d;
            text-decoration: underline;
        }
    </style>
        All rights reserved @2024. Cogent Holdings IT Solutions.      
    </div>
"""
st.markdown(footer_html,unsafe_allow_html=True)
