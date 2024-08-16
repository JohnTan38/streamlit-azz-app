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

#import smtplib, email, ssl
#from email import encoders
#from email.mime.base import MIMEBase
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

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


def process_dataframe(df_data):
    # Function to extract number after last whitespace
    def extract_number(s):
        # Check if the input is string
        if isinstance(s, str):
            try:
                
                return np.float64(re.findall(r'\b\d+\b', s)[-1])
            except (IndexError, ValueError):
                return np.float64(0)
        else:
            return np.float64(0)

    df_data['USED'] = 0

    # Check each column
    for col in df_data.columns:
        try:
            # If the column header is a datetime
            datetime.strptime(str(col), '%Y-%m-%d %H:%M:%S')
            # Apply the function to each element in the column
            df_data['USED'] += df_data[col].apply(extract_number)
        except ValueError:
            continue
            
        df_data['BAL'] = df_data['INITIAL QTY'] - df_data['USED']
        df_data['COST'] = df_data['UNIT $']* df_data['USED']
        df_data['STATUS'] = df_data['BAL'].apply(lambda x: 'REORDER' if x < 5 else 'HEALTHY')

    return df_data

def select_reorder(df):
    return df[df['STATUS'] == 'REORDER']

title_main('PSA Rebates')
#pythoncom.CoInitialize() 

st.sidebar.header("Line graph")
lst_num_week = st.sidebar.multiselect('Select number of weeks to plot', [5,6,7,8,9,10], placeholder='Choose 1', 
                          max_selections=2)
if st.sidebar.button('Confirm weeks'):
    if lst_num_week is not None:
        st.sidebar.write(f'Selected weeks: {lst_num_week[0]}')
        num_week = lst_num_week[0]
    else:
        st.sidebar.write('please select number of weeks')
#if usr_name is not None:
    #if st.sidebar.button('Confirm Username'):
            #usr_email = usr_name[0]+ '@sh-cogent.com.sg' #your outlook email address
            #st.sidebar.write(f'User email: {usr_email}')
            #outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI") 
def user_email(usr_name):
    usr_email = usr_name[0] + '@sh-cogent.com.sg'
    return usr_email

dataUpload = st.file_uploader("Upload your DCON and Week xlsx files", type="xlsx", accept_multiple_files=True)
if dataUpload is None:
        st.text("Please upload a file")
elif dataUpload is not None:
        for i in range(len(dataUpload)):
            if dataUpload[i].name in 'Week.xlsx':
                haulier_original_0 = pd.read_excel(dataUpload[i], sheet_name='Week', engine='openpyxl')
                haulier_00 = haulier_original_0[['ContainerNumber', 'Size,Type', 'CarrierName', 'CarrierVoyage', 'EventType','EventTime']]

                haulier_00.rename(columns = {'ContainerNumber': 'Container_Number', 'CarrierName': 'Carrier_Name', 'CarrierVoyage': 'Carrier_Voyage', 
                            'Size,Type': 'Size', 'EventType': 'Event_Type', 'EventTime': 'Event_Time'}, inplace = True)
                haulier_00.sort_values(['Event_Time', 'Carrier_Name'], ascending=[True, False], inplace=True)
                haulier_0 = haulier_00.copy()
            elif dataUpload[i].name in 'DCON.xlsx':
                dcon_original = pd.read_excel(dataUpload[i], sheet_name='DCON', engine='openpyxl')
                dcon_0 = dcon_original[['Container', 'Discharger Abbreviated Vessel', 'Discharger Abbreviated Voyage', 'Completion of Discharge', 'Exit Time', 
                        'Loader Abbreviated Vessel', 'Loader Abbreviated Voyage', 'Loader Berthing Time', 'Arrive Time']]
                def rename_specific_cols(df, col_to_rename, new_col):
    
                    column_mapping = {col: new_col for col in col_to_rename}
                    df_rename_col = df.rename(columns=column_mapping)
                    return df_rename_col
                #dcon_1 = rename_specific_cols(dcon_0.copy(), ['Discharger Abbreviated Vessel', 'Loader Abbreviated Vessel'], 'Carrier_Name')
                #dcon_2 = rename_specific_cols(dcon_1, ['Discharger Abbreviated Voyage', 'Loader Abbreviated Voyage'], 'Carrier_Voyage')

                dcon_0.rename(columns={'Container': 'Container_Number', 'Discharger Abbreviated Vessel': 'Discharger_Abbr_Vessel', 'Completion of Discharge': 'Complete_Discharge_Time', 'Exit Time': 'Exit_Time', 
                       'Loader Abbreviated Vessel': 'Loader_Abbr_Vessel', 'Loader Berthing Time': 'Loader_Berth_Time', 'Arrive Time': 'Arrive_Time'}, inplace=True)
                def format_time(df, col1,col2):
                    df[col1] = df[col1].astype(str).str.replace('-','')
                    df[col2] = df[col2].astype(str).str.replace('-','')
                    return df
                dcon_1=format_time(dcon_0, 'Exit_Time', 'Arrive_Time')
                dcon_2=format_time(dcon_1, 'Complete_Discharge_Time', 'Loader_Berth_Time')

                def populate_none(df):
                    # Replace empty strings with None in 'Exit_Time' and 'Arrive_Time' columns
                    df['Exit_Time'] = df['Exit_Time'].apply(lambda x: None if x == '' else x)
                    df['Arrive_Time'] = df['Arrive_Time'].apply(lambda x: None if x == '' else x)
                    return df

                def add_event_type_column(df):
                    # Create a new column 'Event_Type' with default value as None
                    df['Event_Type'] = 'ARRIVE'    
    
                    df.loc[df['Exit_Time'].notna(), 'Event_Type'] = 'EXIT' # Assign 'EXIT' if 'Exit_Time' is not empty   
                    #df.loc[df['Arrive_Time'].notna() & df['Event_Type'].isna(), 'Event_Type'] = 'ARRIVE' # Assign 'ARRIVE' if 'Arrive_Time' is not empty and 'Event_Type' is still None
                    return df
                dcon_3 = add_event_type_column(populate_none(dcon_2))

                def format_datetime_columns(df, columns, date_format):
                    for column in columns:
                            df[column] = pd.to_datetime(df[column], format=date_format)
                    return df

                def calculate_time_difference(df):
                    # Calculate Time_Difference based on conditions
                    df['Time_Difference'] = None
                    df.loc[df['Exit_Time'].isna(), 'Time_Difference'] = (df['Loader_Berth_Time'] - df['Arrive_Time']).dt.total_seconds() / 60
                    df.loc[df['Arrive_Time'].isna(), 'Time_Difference'] = (df['Exit_Time'] - df['Complete_Discharge_Time']).dt.total_seconds() / 60
   
                    df['PSA_Rebate'] = np.nan # Initialize a new column 'PSA_Rebate' with NaN values

                    # Assign 'PSA_Rebate' based on 'Time_Difference'
                    df.loc[df['Time_Difference'] < 24*60, 'PSA_Rebate'] = 1
                    df.loc[(df['Time_Difference'] >= 24*60) & (df['Time_Difference'] < 48*60), 'PSA_Rebate'] = 2
                    return df
                psa_rebate_indicator = calculate_time_difference(format_datetime_columns(dcon_3, 
                                                                         ['Complete_Discharge_Time', 'Exit_Time', 'Loader_Berth_Time', 'Arrive_Time'], '%d%m%Y %H:%M'))
                 


                def add_psa_rebate(df_hauler, df_psa_rebate):
                    df_hauler['Event_Time'] = pd.to_datetime(df_hauler['Event_Time']) # Convert to datetime for comparison
                    df_psa_rebate['Exit_Time'] = pd.to_datetime(df_psa_rebate['Exit_Time'])
                    df_psa_rebate['Arrive_Time'] = pd.to_datetime(df_psa_rebate['Arrive_Time'])
    
                    # Merge df_hauler with df_psa_rebate on 'Container_Number' and 'Event_Type'
                    df_merged = pd.merge(df_hauler, df_psa_rebate, on=['Container_Number', 'Event_Type'], how='left')
    
                    # Function to check if Event_Time matches with Complete_Discharge_Time or Loader_Berth_Time
                    def rebate(row):
                        if row['Event_Time'] == row['Exit_Time'] or row['Event_Time'] == row['Arrive_Time']:
                            return row['PSA_Rebate']
                        return None
    
                    # Apply the function to each row
                    df_merged['PSA_Rebate'] = df_merged.apply(rebate, axis=1)
    
                    # Return the original df_hauler DataFrame with the new 'PSA_Rebate' column
                    return df_merged[['Container_Number', 'Size', 'Event_Type', 'Event_Time', 'PSA_Rebate']]
                updates_df_haulier = add_psa_rebate(haulier_0, psa_rebate_indicator)
    
                def rename_duplicate_columns(df):
                    cols = pd.Series(df.columns)
                    for dup in cols[cols.duplicated()].unique(): 
                        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
                    df.columns = cols
                    return df
                from datetime import datetime    
                 
        #def send_email_psa_reabte(df,usr_email):
            #usr_email = user_email(usr_name)
            #email_receiver = usr_email
            ##email_receiver = st.multiselect('Select one email', ['john.tan@sh-cogent.com.sg', 'vieming@yahoo.com'])
            #email_sender = "john.tan@sh-cogent.com.sg"
            #email_password = "Realmadrid8985@" #st.secrets["password"]

            #body = """
                #<html>
                #<head>
                #<title>Dear User</title>
                #</head>
                #<body>
                #<p style="color: blue;font-size:25px;">PSA Rebate ($) offpeak/peak.</strong><br></p>

                #</body>
                #</html>

                #"""+ df.to_html() +"""
        
                #<br>This message is computer generated. """+ datetime.now().strftime("%Y%m%d %H:%M:%S")

            #mailserver = smtplib.SMTP('smtp.office365.com',587)
            #mailserver.ehlo()
            #mailserver.starttls()
            #mailserver.login(email_sender, email_password)
       
            #try:
                #if email_receiver is not None:
                    #try:
                        #rgx = r'^([^@]+)@[^@]+$'
                        #matchObj = re.search(rgx, email_receiver)
                        #if not matchObj is None:
                            #usr = matchObj.group(1)
                    
                    #except:
                        #pass

                #msg = MIMEMultipart()
                #msg['From'] = email_sender
                #msg['To'] = email_receiver
                #msg['Subject'] = 'PSA Rebate Summary '+ datetime.today().strftime("%Y%m%d %H:%M")
                #msg['Cc'] = 'john.tan@sh-cogent.com.sg'
        
                #msg.attach(MIMEText(body, 'html'))
                #text = msg.as_string()

                #with smtplib.SMTP("smtp.office365.com", 587) as server:
                    #server.ehlo()
                    #server.starttls()
                    #server.login(email_sender, email_password)
                    #server.sendmail(email_sender, email_receiver, text)
                    #server.quit()
                #st.success(f"Email sent to {email_receiver} 💌 🚀")
                #success_df(f"Email sent to {email_receiver} 💌 🚀")
            #except Exception as e:
                #st.error(f"Email not sent: {e}")


        if st.button('Lets get rebates'):
            #st.dataframe(data_new)
            st.divider()
            updates_df_haulier = add_psa_rebate(haulier_0, psa_rebate_indicator)
            #psa_rebate_indicator = calculate_time_difference(append_columns_2(dcon,haulier_0).dropna(subset=['Container_Number']))
            #rebate = data_new.copy()
            from datetime import datetime
            
            df_public_holidays = pd.read_excel("https://raw.githubusercontent.com/JohnTan38/Project-Income/main/public_holidays.xlsx", sheet_name='public_holidays', 
                                                engine='openpyxl')
            public_holidays = df_public_holidays['public_holidays'].tolist() # Define the public holidays in Singapore

            def extract_numeric(df):
                df['Size'] = df['Size'].str.extract('(\\d+)', expand=False)  # Use regular expression to extract numeric part of 'Size' column
                return df

            def add_offpeak_columns(df_rebate):
                df_rebate['Event_Time'] = pd.to_datetime(df_rebate['Event_Time'], format='%Y-%m-%d %H:%M:%S') # Convert the 'Event_Time' column to datetime

                # Initialize the 'Offpeak_24' and 'Offpeak_48' columns with 0
                df_rebate['Offpeak_24'] = 0
                df_rebate['Offpeak_48'] = 0

                # Iterate over the rows of the DataFrame
                for i, row in df_rebate.iterrows():
                    # Check if the event time is a Sunday, a public holiday, or between 21:00 and 04:59
                    if row['Event_Time'].weekday() == 6 or row['Event_Time'].strftime('%Y-%m-%d') in public_holidays or (row['Event_Time'].hour >= 21 or row['Event_Time'].hour < 5):
                        # If 'PSA_Rebate' is 1, set 'Offpeak_24' to 1
                        if row['PSA_Rebate'] == 1.0:
                            df_rebate.at[i, 'Offpeak_24'] = 1
                        # If 'PSA_Rebate' is 2, set 'Offpeak_48' to 1
                        elif row['PSA_Rebate'] == 2.0:
                            df_rebate.at[i, 'Offpeak_48'] = 1
    
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
            
            #total rebate    
            def calculate_rebate(df):
                # Define a function to calculate rebate based on the conditions
                def rebate(row):
                    #if row['Offpeak_24'] == 1:
                        if row['Size'] == '20':
                            return offpeak_20_24 if row['Offpeak_24'] == 1 else offpeak_20_48 if row['Offpeak_48'] == 1 else 0
                        elif row['Size'] == '40':
                            return offpeak_40_24 if row['Offpeak_24'] == 1 else offpeak_40_48 if row['Offpeak_48'] == 1 else 0
            
                    #elif row['Nonpeak'] == 'No':
                        if row['Size'] == '20':
                            return peak_20_24 if row['Peak_24'] == 1 else peak_20_48 if row['Peak_48'] == 1 else 0
                        elif row['Size'] == '40':
                            return peak_40_24 if row['Peak_24'] == 1 else peak_40_48 if row['Peak_48'] == 1 else 0
                        else:
                            return 0

                # Apply the function to each row in the DataFrame to calculate the rebate
                df['Rebate'] = df.apply(rebate, axis=1)
                return df
            st.dataframe(calculate_rebate(add_offpeak_columns(updates_df_haulier)))
            st.divider()

            def count_occurrences(df_rebate):
                # Initialize a new DataFrame with the desired index and columns
                df_count = pd.DataFrame(index=['20', '40'], columns=['Offpeak_24', 'Offpeak_48'])

                # Count the occurrences and fill the new DataFrame
                for size in ['20', '40']:
                    for offpeak in ['Offpeak_24', 'Offpeak_48']:
                        df_count.at[size, offpeak] = df_rebate[(df_rebate['Size'] == size) & (df_rebate[offpeak] == 1)].shape[0]

                return df_count
            st.write("20 ft/40 ft offpeak count")
            st.table(count_occurrences(calculate_rebate(add_offpeak_columns(updates_df_haulier))))
            psa_offpeak_count = count_occurrences(calculate_rebate(add_offpeak_columns(updates_df_haulier)))

            def offpeak_rebate_sums(df_rebate):
                # Filter rows based on conditions
                offpeak_20_24 = df_rebate[(df_rebate['Size'] == '20') & (df_rebate['Offpeak_24'] == 1)]['Rebate'].sum()
                offpeak_40_24 = df_rebate[(df_rebate['Size'] == '40') & (df_rebate['Offpeak_24'] == 1)]['Rebate'].sum()
                offpeak_20_48 = df_rebate[(df_rebate['Size'] == '20') & (df_rebate['Offpeak_48'] == 1)]['Rebate'].sum()
                offpeak_40_48 = df_rebate[(df_rebate['Size'] == '40') & (df_rebate['Offpeak_48'] == 1)]['Rebate'].sum()

                # Create a new DataFrame with the calculated sums
                offpeak_df = pd.DataFrame({
                    'offpeak_24hr': [offpeak_20_24, offpeak_40_24],
                    'offpeak_48hr': [offpeak_20_48, offpeak_40_48]
                    }, index=['20', '40'])

                return offpeak_df
            st.write("Offpeak Rebates ($)")
            st.dataframe(offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(updates_df_haulier))))

            def sum_and_round(df):
                column_sums = df.sum() #sum all cols
                rounded_sums = column_sums.round(1)
                return rounded_sums

            sums = sum_and_round(offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(updates_df_haulier))))
            #st.write(f"total_offpeak_rebate_24hr: {sums['offpeak_24hr']}") #st.write(f"total_offpeak_rebate_48hr: {sums['offpeak_48hr']}")
            df_offpeak_rebate_sums = offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(updates_df_haulier)))
            
            #20240801
            df_overall_rebate_efficiency = pd.read_excel(r'https://raw.githubusercontent.com/JohnTan38/Project-Income/main/Overall_Rebate_Efficiency.xlsx', sheet_name='OverallRebateEfficiency', 
                                 engine='openpyxl')
            df_psa_lolo = pd.read_excel(r'https://raw.githubusercontent.com/JohnTan38/Project-Income/main/Overall_Rebate_Efficiency.xlsx', sheet_name='PSA_LOLO',
                             engine='openpyxl')
            df_overall_rebate_efficiency.set_index('Week', inplace=True)
            psa_lolo_20 = df_psa_lolo['psa_lolo_20']
            psa_lolo_40 = df_psa_lolo['psa_lolo_40']
            #sum across cols
            def sum_cols(df, col_sum):
                df[col_sum] = df.sum(axis=1)
                return df
            
            df_rebate_total=sum_cols(df_offpeak_rebate_sums, 'sum_offpeak_rebate')

            rebate_efficiency_20 = (df_rebate_total['sum_offpeak_rebate']['20'] /psa_lolo_20) /0.5932
            rebate_efficiency_40 = (df_rebate_total['sum_offpeak_rebate']['40'] /psa_lolo_40) /0.5932
            overall_rebate_efficiency = math.ceil(((rebate_efficiency_20+rebate_efficiency_40)/2)*100) /100 #round 2 decimals

            def add_column(df,new_week):
                last_column = df.columns[-1]
                last_week_number = int(last_column.split('_')[-1]) #get week number of last col
                new_column = 'Week_'+ str(last_week_number+1)
                df[new_column] = new_week
                return df

            import datetime
            today_date = datetime.datetime.today().strftime('%Y-%m-%d) #format as str
            date = datetime.datetime.strptime(today_date, '%Y-%m-%d)
            week_num = date.isocalendar()[1] #get week num of current date

            def get_week_number(df_rebate_efficiency):
                last_week_label = df_rebate_efficiency['Week'].iloc[-1] #get the last week label
                week_number = int(last_week_label.split('_')[-1])
                return week_number
            if week_num != get_week_number(df_overall_rebate_efficiency.reset_index()):
                df_overall_rebate_efficiency_new = add_column(df_overall_rebate_efficiency.T, overall_rebate_efficiency)
            else:
                df_overall_rebate_efficiency_new = df_overall_rebate_efficiency.T
            
            #df_overall_rebate_efficiency_new = add_column(df_overall_rebate_efficiency.T, overall_rebate_efficiency) #original code
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
                
            def plot_clustered_bar(df, df_rebate):
                # Set the color palette as gradient from light blue to dark blue
                sns.set_palette(sns.color_palette("Blues", len(df.columns)))
    
                fig, ax = plt.subplots() # Create a figure and a set of subplots
                # Plot the DataFrame as a bar plot with the specified parameters
                df.plot(kind='bar', ax=ax)

                # Append column values of df_rebate to the respective bar charts
                for i, p in enumerate(ax.patches):
                    ax.annotate(str(df_rebate.iloc[i//len(df.columns), i%len(df.columns)]), 
                               (p.get_x() * 1.005, p.get_height() * 1.005))
    
                dynamic_max_value = max(int(df.max().max()), 450)
                plt.ylim(0, dynamic_max_value + dynamic_max_value*0.15)) # Set the dynamic y-axis limit
                #plt.ylim(0, 450)     
                plt.title('Nonpeak - container volume and $rebate', fontsize=9) # Set the title of the plot
                plt.ylabel('Container volume and $rebate', fontsize=8)
                plt.xlabel('Container size', fontsize=8)   
                #plt.show() # Show the plot
                st.pyplot(fig,ax)

            df_offpeak_rebate_sums_dollar = append_dollar(df_offpeak_rebate_sums)
            plot_clustered_bar(psa_offpeak_count, (df_offpeak_rebate_sums_dollar.iloc[:, :-1]).T) #call the function


            html_str_offpeak_rebate24 = f"""
                <p style='background-color:#F0FFFF;
                color: #483D8B;
                font-size: 18px;
                font: bold;
                border-radius:5px;
                padding-left: 12px;
                padding-top: 10px;
                padding-bottom: 12px;
                line-height: 18px;
                border-color: #03396c;
                text-align: left;'>
                {sums['offpeak_24hr']}</style>
                <br></p>"""
            st.markdown('''
                **TOTAL OFFPEAK REBATES ($) < 24hr** '''+html_str_offpeak_rebate24, unsafe_allow_html=True)
            
            html_str_offpeak_rebate48 = f"""
                <p style='background-color:#F0FFFF;
                color: #483D8B;
                font-size: 18px;
                font: bold;
                border-radius:5px;
                padding-left: 12px;
                padding-top: 10px;
                padding-bottom: 12px;
                line-height: 18px;
                border-color: #03396c;
                text-align: left;'>
                {sums['offpeak_48hr']}</style>
                <br></p>"""
            st.markdown('''
                **24hr < TOTAL OFFPEAK REBATES ($) < 48hr** '''+html_str_offpeak_rebate48, unsafe_allow_html=True)

            success_df('Data generated successfully!')
#st.markdown('''
            #**REBATES** :orange[rebates] :blue-background[blue highlight] :cherry_blossom:''')

            #sheetName = 'psa_rebate_'+ datetime.now().strftime("%Y%m%d %H%M")
            #try:
                    #calculate_rebate(add_offpeak_columns(psa_rebate_indicator)).to_csv("C:/Users/"+usr_name[0]+ "/Downloads/"+ 'psa_rebate.csv', mode='x')
            #except FileExistsError:
                    #calculate_rebate(add_offpeak_columns(psa_rebate_indicator)).to_csv("C:/Users/"+usr_name[0]+ "/Downloads/"+ 'psa_rebate_1.csv')
            
            #usr_email = user_email(usr_name)
            #send_email_psa_reabte(offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(psa_rebate_indicator))),usr_email)


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
