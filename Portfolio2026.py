import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Page config
st.set_page_config(page_title="Sameer's Portfolio Tracker", layout="wide", page_icon="📊")
st.title("📊 Sameer's Portfolio Tracker – Rajasthan Restaurants")
st.markdown("**Interactive AI-Driven Dashboard** | MoM Trends, Restaurant Insights | Upload CSVs for full data")

# Built-in demo data (from your shared CSVs – truncated)
monthly_data_str = """
,,2025-07,2025-08,2025-09,2025-10,2025-11,2025-12,2026-01,2026-02,2026-03
Orders,Total_OV,12131,15374,14152,15200,13936,15060,16962,15493,8539
,Ads_ov,3237,4069,3709,3819,5392,7469,8511,9522,5407
,Ads_ov%,26.68%,26.47%,26.21%,25.13%,38.69%,49.59%,50.18%,61.46%,63.32%
Revenue,Subtotal Value,4190088,5472950,5031388,5671928,4897425,5415835,5837830,5314038,3005760
,PC,29635,34297,38251,33995,29669,38307,47282,41050,25868
,Subtotal+PC,4219722,5507248,5069640,5705924,4927095,5454142,5885112,5355088,3031628
,CV,3281877,4073163,3627935,4276811,3686141,4100899,4509484,4152037,2345242
,GMV,4687002,6097418,5609099,6297233,5453290,6030471,6512704,5933419,3354231
,ACV,271,265,256,281,265,272,266,268,275
,AOV,386,397,396,414,391,400,384,383,393
,MVD,677823,739525,644094,768963,657168,760835,843438,683130,411472
,MVD Discount%,16.18%,13.51%,12.80%,13.56%,13.42%,14.05%,14.45%,12.86%,13.69%
,MVDPO,56,48,46,51,47,51,50,44,48
,Salt,218854,647387,761163,611190,542317,547822,473148,480706,248833
,Salt Discount %,5.22%,11.83%,15.13%,10.78%,11.07%,10.12%,8.10%,9.05%,8.28%
,SALTPO,18,42,54,40,39,36,28,31,29
,ZVD,137919,158593,122549,137336,141211,189733,262808,225087,144906
,ZVD Discount %,3.29%,2.90%,2.44%,2.42%,2.88%,3.50%,4.50%,4.24%,4.82%
,ZVDPO,11,10,9,9,10,13,15,15,17
Funnel metrics,Impression,1326897,1558263,1481266,1518542,1393981,1498802,1799532,1735330,909383
,Menu Opens,119293,143779,131779,135784,128816,134046,154025,143183,73873
,Cart builds,34900,44421,42365,43992,42142,44448,50517,45701,23905
,Order makes,14330,18306,16935,18070,16525,17855,20025,18284,9919
,M2C,29.26%,30.90%,32.15%,32.40%,32.71%,33.16%,32.80%,31.92%,32.36%
,C2O,41.06%,41.21%,39.97%,41.08%,39.21%,40.17%,39.64%,40.01%,41.49%
,M2O,12.01%,12.73%,12.85%,13.31%,12.83%,13.32%,13.00%,12.77%,13.43%
,BF MO,4306,5776,5282,5671,4518,4406,4760,4479,2274
,BF CB,826,1232,1116,1145,1063,1005,1183,1033,489
,BF OM,291,451,400,439,427,386,477,429,208
,BF_M2C,19.18%,21.33%,21.13%,20.19%,23.53%,22.81%,24.85%,23.06%,21.50%
,BF_C2O,35.23%,36.61%,35.84%,38.34%,40.17%,38.41%,40.32%,41.53%,42.54%
,BF_M2O,6.76%,7.81%,7.57%,7.74%,9.45%,8.76%,10.02%,9.58%,9.15%
,Lunch MO,29176,35917,32198,30724,26595,27619,30780,31299,17344
,Lunch CB,8619,11187,10398,10102,8936,9205,9936,9819,5382
,Lunch OM,3434,4469,4139,4067,3522,3600,3850,3847,2158
,Lunch_M2C,29.54%,31.15%,32.29%,32.88%,33.60%,33.33%,32.28%,31.37%,31.03%
,Lunch_C2O,39.84%,39.95%,39.81%,40.26%,39.41%,39.11%,38.75%,39.18%,40.10%
,Lunch_M2O,11.77%,12.44%,12.85%,13.24%,13.24%,13.03%,12.51%,12.29%,12.44%
,Sn MO,13130,14730,13425,13296,12659,14882,17188,15725,8339
,SN CB,3544,4123,4111,4043,3965,4513,5099,4594,2477
,SN OM,1276,1425,1391,1459,1409,1525,1679,1550,858
,Snacks_M2C,26.99%,27.99%,30.62%,30.41%,31.32%,30.33%,29.67%,29.21%,29.70%
,Snacks_C2O,36.00%,34.56%,33.84%,36.09%,35.54%,33.79%,32.93%,33.74%,34.64%
,Snacks_M2O,9.72%,9.67%,10.36%,10.97%,11.13%,10.25%,9.77%,9.86%,10.29%
,Dinner MO,58738,66516,62635,67477,69453,71260,85278,75696,37060
,Dinner CB,17954,21761,21124,23020,23496,24609,29111,25005,12634
,Dinner OM,7719,9377,8755,9753,9314,10112,11888,10299,5458
,Dinner_M2C,30.57%,32.72%,33.73%,34.12%,33.83%,34.53%,34.14%,33.03%,34.09%
,Dinner_C2O,42.99%,43.09%,41.45%,42.37%,39.64%,41.09%,40.84%,41.19%,43.20%
,Dinner_M2O,13.14%,14.10%,13.98%,14.45%,13.41%,14.19%,13.94%,13.61%,14.73%
,LN MO,13943,20840,18239,18616,15591,15879,16019,15984,8856
,LN CB,3957,6118,5616,5682,4682,5116,5188,5250,2923
,LN OM,1610,2584,2250,2352,1853,2232,2131,2159,1237
,ln_M2C,28.38%,29.36%,30.79%,30.52%,30.03%,32.22%,32.39%,32.85%,33.01%
,ln_C2O,40.69%,42.24%,40.06%,41.39%,39.58%,43.63%,41.08%,41.12%,42.32%
,ln_M2O,11.55%,12.40%,12.34%,12.63%,11.89%,14.06%,13.30%,13.51%,13.97%
Advertisement,Ads CV,832414,984264,885332,1035102,1397077,1904509,2142509,2407730,2407730
,Ads/CV,6.51%,6.07%,6.47%,5.66%,8.44%,10.52%,11.43%,12.99%,12.99%
,Ads Impression,535695,623390,581664,546252,681577,857302,1116290,1224717,1224717
,Ads Impression%,40.37%,40.01%,39.27%,35.97%,48.89%,57.20%,62.03%,70.58%,70.58%
,Ad Menu Opens,41368,48010,42319,58135,57518,72541,88152,95017,95017
,Ad Menu Opens%,34.68%,33.39%,32.11%,42.81%,44.65%,54.12%,57.23%,66.36%,66.36%
,Ad Orders,3237,4069,3709,3819,5392,7469,8511,9522,9522
,Ad Orders%,26.68%,26.47%,26.21%,25.13%,38.69%,49.59%,50.18%,61.46%,61.46%
,Ads M2O,7.82%,8.48%,8.76%,6.57%,9.37%,10.30%,9.65%,10.02%,10.02%
,Ads booked,278287,348274,395271,492519,632120,845683,970697,1095659,1095659
,Ads Billed (spend),213668,247086,234885,242149,311268,431608,515400,539526,539526
,Ads Delivery %,76.78%,70.95%,59.42%,49.17%,49.24%,51.04%,53.10%,49.24%,49.24%
,Ads Billed (spend) %,5.06%,4.49%,4.63%,4.24%,6.32%,7.91%,8.76%,10.08%,10.08%
,ARPO,18,16,17,16,22,29,30,35,35
,Ads GMV,1073775,1370134,1296728,1405324,1893783,2633164,2846978,3174738,3174738
,Total spend (ads + disc)%,26.46%,29.83%,32.56%,28.58%,30.81%,32.08%,31.31%,31.98%,31.98%
,Ads ROI,4,4,4,4,4,4,4,4,4
Mealtime OV,BreakFast,1.91%,2.22%,2.22%,2.16%,2.34%,2.04%,2.25%,2.27%,2.27%
,Lunch,23.53%,24.44%,24.17%,22.44%,21.45%,20.15%,19.31%,21.04%,21.04%
,Snacks,8.43%,7.49%,7.89%,8.03%,8.35%,8.28%,8.15%,8.29%,8.29%
,Dinner,55.70%,52.53%,53.12%,55.00%,57.46%,57.62%,60.17%,57.21%,57.21%
,Late Night,10.42%,13.31%,12.60%,12.36%,10.40%,11.91%,10.12%,11.20%,11.20%
Customer segment,la_orders,65.52%,67.70%,68.40%,69.45%,69.51%,70.60%,72.84%,71.04%,71.04%
,mm_orders,16.17%,16.25%,16.18%,15.37%,16.17%,15.61%,14.40%,15.43%,15.43%
,um_orders,18.31%,16.05%,15.42%,15.18%,14.32%,13.78%,12.76%,13.54%,13.54%
AOV Bucket,Less_than_50_ov,0.15%,0.08%,0.05%,0.04%,0.17%,0.09%,0.06%,0.09%,0.09%
,Bw_50_100_ov,2.19%,2.02%,2.05%,1.80%,1.82%,1.88%,2.10%,2.48%,2.48%
,Bw_100_150,5.49%,5.72%,5.59%,5.72%,5.72%,5.84%,6.35%,6.96%,6.96%
,Bw_150_200,11.29%,12.16%,13.60%,13.11%,15.21%,14.39%,17.09%,16.70%,16.70%
,Bw_200_250,16.96%,15.77%,16.39%,14.98%,14.36%,15.61%,15.96%,14.68%,14.68%
,Bw_250_300,17.15%,15.47%,14.01%,14.20%,14.14%,14.23%,13.55%,14.01%,14.01%
,Bw_300_350,13.23%,12.92%,12.11%,12.01%,12.63%,12.08%,11.54%,11.23%,11.23%
,Bw_350_400,8.99%,9.31%,8.62%,8.27%,8.54%,8.14%,7.94%,8.16%,8.16%
,Bw_400_450,5.65%,5.45%,6.06%,6.33%,6.38%,6.01%,5.46%,4.94%,4.94%
,Bw_450_500,4.36%,4.70%,4.86%,4.34%,4.61%,4.31%,4.14%,4.78%,4.78%
,Bw_500_700,9.12%,9.85%,10.08%,10.99%,10.65%,10.73%,9.83%,9.93%,9.93%
,Bw_700_900,3.07%,3.71%,3.71%,4.26%,3.23%,3.68%,3.10%,3.41%,3.41%
,Bw_900_1200,1.53%,1.78%,1.80%,2.44%,1.58%,1.83%,1.69%,1.73%,1.73%
,Above_1200,0.83%,1.03%,1.07%,1.51%,0.98%,1.18%,1.20%,0.89%,0.89%
Organic ,Organic Orders,8894,11305,10443,11381,8544,7591,8451,5971,5971
,Organic Orders%,73.32%,73.53%,73.79%,74.88%,61.31%,50.41%,49.82%,38.54%,38.54%
,Organic MO's,77925,95769,89460,77649,71298,61505,65873,48166,48166
,Organic MO's%,65.32%,66.61%,67.89%,57.19%,55.35%,45.88%,42.77%,33.64%,33.64%
Distance OV,Null Distance ov,4.31%,3.50%,3.69%,3.89%,3.27%,3.32%,3.44%,3.68%,3.68%
,0_3km_ov,41.76%,38.92%,40.55%,40.40%,42.11%,41.57%,44.51%,44.29%,44.29%
,3_4km_ov,14.57%,15.70%,15.57%,16.38%,16.35%,15.94%,16.21%,15.47%,15.47%
,4_5km_ov,13.07%,14.11%,13.11%,11.89%,12.05%,12.07%,12.36%,12.97%,12.97%
,5_7km_ov,16.78%,17.68%,17.06%,17.51%,17.27%,17.88%,15.29%,15.97%,15.97%
,7_10km_ov,8.67%,9.27%,8.86%,8.88%,8.05%,8.38%,7.43%,6.95%,6.95%
,>10km_ov,0.83%,0.83%,1.15%,1.05%,0.90%,0.85%,0.77%,0.66%,0.66%
"""

res_data_str = """
Aggregation,city_name,subzone,res_name,lvl,Total_ov,res_cuisine_new
1/1/2026,Ajmer,All_subzone,Life Is Tea,19527478,21,street food
1/1/2026,Kota,All_subzone,Cakey 'N' Bakey,18857028,47,cakes
12/1/2025,Kota,All_subzone,Jain Fast Foods,19703987,,na
2/1/2026,Kota,All_subzone,Paratha Aunty,22530629,4,north indian
12/1/2025,Kota,All_subzone,Shere Punjab Ice Cream,21729857,,ice cream
11/1/2025,Jodhpur,All_subzone,21st Fast Food,18947351,7,international
12/1/2025,Jodhpur,All_subzone,Hari Vedas,18696027,347,north indian
1/1/2026,Jodhpur,All_subzone,Indie Restaurant,19901397,,na
1/1/2026,Kota,All_subzone,Golgappa King,21465488,,na
2/1/2026,Kota,All_subzone,subway,20696973,576,"wraps, rolls and sandwiches"
11/1/2025,Jodhpur,All_subzone,Gangana Late Night Food,21019904,,na
11/1/2025,Kota,All_subzone,Barbeque Nation,19006643,565,north indian
11/1/2025,Kota,All_subzone,Chaiwala Cafe Bar,21462385,19,chinese
2/1/2026,Jodhpur,All_subzone,Vijay Juice Corner,19155934,100,beverages
1/1/2026,Jodhpur,All_subzone,Momo's Wala,19859957,12,street food
2/1/2026,Ajmer,All_subzone,Shree Shyam Fast food,21215632,,street food
11/1/2025,Jodhpur,All_subzone,Delhi 6 Momos,18974083,11,street food
11/1/2025,Jodhpur,All_subzone,Poker Midnight,20871393,,na
1/1/2026,Ajmer,All_subzone,Ajanta Street Chinese,22451621,,na
12/1/2025,Jodhpur,All_subzone,Get A Lassi,20846294,,na
1/1/2026,Jodhpur,All_subzone,Balaji Bite Corner,21724491,,na
12/1/2025,Kota,All_subzone,Urban Punjabi Foods,20204962,138,north indian
2/1/2026,Jodhpur,All_subzone,Satguru Vada Pav & Fast Food,21265580,49,street food
1/1/2026,Ajmer,All_subzone,Jain Tiffin Center,20239441,,na
12/1/2025,Kota,All_subzone,London Coffee,21364412,,beverages
2/1/2026,Ajmer,All_subzone,Tiny Morsel Snacks & Beverages,21042373,,na
12/1/2025,Kota,All_subzone,Home Delivery Bakery,21010472,,cakes
2/1/2026,Kota,All_subzone,Polo Restaurant,18706645,13,north indian
2/1/2026,Jodhpur,All_subzone,Kerala Vridavan,22196656,86,north indian
11/1/2025,Kota,All_subzone,The Bakers,20925618,,cakes
1/1/2026,Ajmer,All_subzone,The Great Indian Food Kitchen,20711646,11,beverages
12/1/2025,Kota,All_subzone,domino's pizza irctc,22148202,90,pizza
11/1/2025,Kota,All_subzone,Navras Dairy,22195305,49,beverages
12/1/2025,Kota,All_subzone,Five Star Paratha,19667712,,na
11/1/2025,Kota,All_subzone,Delhi Roll's,21177540,9,"wraps, rolls and sandwiches"
12/1/2025,Kota,All_subzone,The Mother's Home,20253059,,na
11/1/2025,Jodhpur,All_subzone,Hamza Ahmedabad Chicken Chinese,18946567,,na
2/1/2026,Kota,All_subzone,Chinese Wok,21523163,,chinese
1/1/2026,Udaipur,All_subzone,Golden Sweets And Bakery,20850770,,na
12/1/2025,Jodhpur,All_subzone,domino's pizza irctc,22047675,19,pizza
11/1/2025,Jodhpur,All_subzone,Saffron Bites,22161318,7,north indian
12/1/2025,Jodhpur,All_subzone,Fresh Meat,19744072,,na
2/1/2026,Jodhpur,All_subzone,Crazy Grills - Cloud Kitchen,22087963,,na
12/1/2025,Jodhpur,All_subzone,Chai And Nasta,21765276,3,beverages
1/1/2026,Jodhpur,All_subzone,Chai And Nasta,21765276,2,beverages
1/1/2026,Kota,All_subzone,Anand Shekhawati Foods,21750424,,na
12/1/2025,Ajmer,All_subzone,The Pakwan Wala,22102579,1,north indian
12/1/2025,Udaipur,All_subzone,Kwality Bakery,19720210,740,street food
1/1/2026,Ajmer,All_subzone,The Pakwan Wala,22102579,,north indian
1/1/2026,Jodhpur,All_subzone,Shree Ram Fast Food And Restaurant,21356499,159,north indian
1/1/2026,Jodhpur,All_subzone,Jodhpuri Delights,21627305,,na
12/1/2025,Ajmer,All_subzone,Delights By Inox,21839755,3,street food
2/1/2026,Ajmer,All_subzone,Jannat Restaurant,18690050,,north indian
11/1/2025,Kota,All_subzone,Chicken Bite,19759966,15,international
2/1/2026,Jodhpur,All_subzone,Arnicas Bakery,22385211,,cakes
1/1/2026,Jodhpur,All_subzone,Pizza 29,22165952,,na
12/1/2025,Kota,All_subzone,Rollx,18871211,,"wraps, rolls and sandwiches"
2/1/2026,Kota,All_subzone,Madras Hotel,18946322,723,south indian
2/1/2026,Jodhpur,All_subzone,Rani Bhatiyani Bhojnalya and Sweet Home,20323345,42,north indian
12/1/2025,Udaipur,All_subzone,97 Creation Bakery And Cafe,22190324,13,desserts
2/1/2026,Kota,All_subzone,Hot Corner Fast Food,21979216,,na
11/1/2025,Kota,All_subzone,Scoop whoop,19991509,,na
1/1/2026,Jodhpur,All_subzone,Shandar Dhaba,19283675,814,north indian
12/1/2025,Udaipur,All_subzone,The Kanha Cafe And Restro,21573338,,na
1/1/2026,Kota,All_subzone,Cafe Mellow,20158192,68,pizza
12/1/2025,Ajmer,All_subzone,Natural Bakers,19624189,10,na
2/1/2026,Ajmer,All_subzone,V TUTUS Veg/Non Veg Mobile Restaurant,19174256,90,north indian
12/1/2025,Kota,All_subzone,Krishna Restaurant,20302180,,north indian
1/1/2026,Udaipur,All_subzone,Paramount Sigdi Dosa,20888866,,na
1/1/2026,Ajmer,All_subzone,Romins Pizza,21587445,157,pizza
2/1/2026,Udaipur,All_subzone,Hari Garh Restaurant,18022652,,na
1/1/2026,Jodhpur,All_subzone,Sanwhich,20764348,50,"wraps, rolls and sandwiches"
1/1/2026,Jodhpur,All_subzone,Yuvraj Kitchen,20347370,,na
2/1/2026,Udaipur,All_subzone,Choube Ji Chole Bhature,19912401,,na
1/1/2026,Udaipur,All_subzone,JMB Jai Mishthan Bhandar & Fast Food,19564002,371,mithai
1/1/2026,Kota,All_subzone,The Wings,19635978,186,street food
2/1/2026,Ajmer,All_subzone,Royal Rajasthani,22112404,,na
2/1/2026,Ajmer,All_subzone,Sindh Punjab Dhaba,18691221,71,north indian
1/1/2026,Jodhpur,All_subzone,99 Variety Dosa,20834637,454,south indian
12/1/2025,Ajmer,All_subzone,Burgerlicious,19528325,493,burger
2/1/2026,Ajmer,All_subzone,Ajmeri Bakery And Pastry Hub,21326877,,na
11/1/2025,Udaipur,All_subzone,JJ's Healthy Time,19486023,153,beverages
11/1/2025,Jodhpur,All_subzone,ACE Food Zone,20804003,,na
2/1/2026,Kota,All_subzone,Bunzo Patties & Sandwich,22259387,,na
12/1/2025,Udaipur,All_subzone,Mr Chaap,19701932,414,street food
2/1/2026,Udaipur,All_subzone,Shreeram Fastfood & Chinese,21620778,,na
1/1/2026,Kota,All_subzone,Food Garage,22355440,4,"wraps, rolls and sandwiches"
2/1/2026,Kota,All_subzone,Shree Shyam Paratha And Foods,22469928,,na
11/1/2025,Udaipur,All_subzone,V Cafe - Meals By PVR,21725805,14,street food
2/1/2026,Kota,All_subzone,Fast Food By Paras,20575276,,na
12/1/2025,Udaipur,All_subzone,Poppy by Royal Repast,18246958,254,north indian
12/1/2025,Kota,All_subzone,The Coffee Shop,20845834,,chinese
12/1/2025,Jodhpur,All_subzone,Mellow Bites,22031933,7,north indian
11/1/2025,Jodhpur,All_subzone,Prajapat Tifin Service,19967759,,na
11/1/2025,Jodhpur,All_subzone,Ande Ka Funda,19584911,,north indian
1/1/2026,Kota,All_subzone,Rominus Pizza And Burger,19021431,3210,pizza
2/1/2026,Kota,All_subzone,The Champaran Essence,22129908,2,north indian
12/1/2025,Kota,All_subzone,Amrit Rasoi,22076424,,north indian
11/1/2025,Jodhpur,All_subzone,Chocolicious By Vidhi,21265602,,na
1/1/2026,Udaipur,All_subzone,Sun & Moon Restaurant,18038173,,na
1/1/2026,Kota,All_subzone,D' Food Hub - Veg & Non Veg Restaurant,19713496,50,na
12/1/2025,Jodhpur,All_subzone,Chai Sutta Bar,19757684,59,beverages
1/1/2026,Udaipur,All_subzone,Lykke Restaurant,20900350,1,na
2/1/2026,Kota,All_subzone,Malabar Non Veg Dhaba,22357446,24,north indian
2/1/2026,Udaipur,All_subzone,New Santosh Bhojanalaya,18051392,2,north indian
12/1/2025,Jodhpur,All_subzone,South Indian Chatkara,21270312,16,south indian
12/1/2025,Kota,All_subzone,Rising Bowl,18885814,926,chinese
12/1/2025,Kota,All_subzone,Aman Punjabi Dhaba,21975943,,na
2/1/2026,Jodhpur,All_subzone,Urban Theka,20844729,,street food
12/1/2025,Udaipur,All_subzone,Food-O-Logy,20635094,,na
12/1/2025,Jodhpur,All_subzone,Shri Ram Restaurant,19664124,,north indian
11/1/2025,Ajmer,All_subzone,Hotel Atlantica,18927483,141,north indian
12/1/2025,Jodhpur,All_subzone,Arora's Food Zone,22115269,,na
11/1/2025,Udaipur,All_subzone,Little Italy,19240513,127,international
2/1/2026,Jodhpur,All_subzone,Goli Vada Pav No. 1,21121591,,street food
2/1/2026,Udaipur,All_subzone,Angethi By Udaipur Restaurant,22549090,,street food
2/1/2026,Kota,All_subzone,Mumbai Bistro,20555632,,street food
12/1/2025,Udaipur,All_subzone,Kavita Pav Bhaji & Chinese,21531788,,chinese
11/1/2025,Udaipur,All_subzone,Seven Lakes Cafe And Restaurant,20625766,,north indian
12/1/2025,Jodhpur,All_subzone,Chicken Chasers,20652402,116,north indian
2/1/2026,Jodhpur,All_subzone,the belgian waffle co.,18694900,937,desserts
11/1/2025,Kota,All_subzone,Bihari Meat House,21853612,737,north indian
1/1/2026,Jodhpur,All_subzone,Tom And Jerry Fast Food And Bakery,19271169,3,cakes
1/1/2026,Udaipur,All_subzone,Khana Khazana,21343403,64,north indian
2/1/2026,Jodhpur,All_subzone,Jain Food,20325533,,north indian
11/1/2025,Jodhpur,All_subzone,Tandoori Junction,19752570,119,north indian
1/1/2026,Kota,All_subzone,Hotel Arogya Palace,20753001,1,na
2/1/2026,Kota,All_subzone,Cake Dessert,20896881,1,cakes
2/1/2026,Udaipur,All_subzone,Tasty Tracks,22235876,2,beverages
11/1/2025,Jodhpur,All_subzone,Delhi Chatka,19417571,908,north indian
1/1/2026,Jodhpur,All_subzone,Jai Bhawani Dal Bati Churma,20715420,166,north indian
11/1/2025,Ajmer,All_subzone,Malana Sports Cafe,21086336,,na
1/1/2026,Udaipur,All_subzone,Cake Surprise,20523564,6,cakes
2/1/2026,Udaipur,All_subzone,Midnight Meals,22137364,,street food
12/1/2025,Kota,All_subzone,Sindhi Sweets,22207402,2,mithai
12/1/2025,Jodhpur,All_subzone,Paris Bakery,21293685,8,cakes
12/1/2025,Jodhpur,All_subzone,Dost Ki Tapri Fast Food & Beverages,21914007,494,pizza
1/1/2026,Jodhpur,All_subzone,Beans & Greens,20167578,,na
1/1/2026,Jodhpur,All_subzone,TG Cafe,20872929,,na
1/1/2026,Jodhpur,All_subzone,domino's pizza,21899396,218,pizza
11/1/2025,Jodhpur,All_subzone,The Blue City Kitchen,19347238,,na
11/1/2025,Udaipur,All_subzone,Cafe Soni's,18811728,65,burger
1/1/2026,Kota,All_subzone,Krish Bakers And Cafe,20447918,,na
12/1/2025,Kota,All_subzone,Charcoal,19984447,,north indian
1/1/2026,Kota,All_subzone,Taste Heaven,22265163,,north indian
2/1/2026,Kota,All_subzone,Sai Bakery,20506595,,cakes
12/1/2025,Kota,All_subzone,Baskin Robbins - Ice Cream Desserts,20445866,73,ice cream
2/1/2026,Udaipur,All_subzone,SBD-Sawliya Burger Dabeli,19738144,22,street food
11/1/2025,Jodhpur,All_subzone,Ayaansh Cloud Kitchen - ACK,21731821,,na
1/1/2026,Udaipur,All_subzone,Momo Master,22239985,,street food
11/1/2025,Ajmer,All_subzone,FPF- Coffee Wala Bhaiya,21572890,217,beverages
12/1/2025,Jodhpur,All_subzone,Kim 15 A.D,18697254,,na
12/1/2025,Kota,All_subzone,Maggi Pit Stop,20698495,16,street food
12/1/2025,Kota,All_subzone,The Liquid Chef,20298101,,na
2/1/2026,Kota,All_subzone,Royal Chicken,19026727,42,north indian
11/1/2025,Kota,All_subzone,Mumbai Sandwiches & More,19390863,,na
12/1/2025,Kota,All_subzone,Anu's Cake Creation,19313949,307,cakes
2/1/2026,Udaipur,All_subzone,Hungry Hub,21163641,,pizza
12/1/2025,Jodhpur,All_subzone,Burger Story,21419244,20,burger
12/1/2025,Kota,All_subzone,Momos Ka Adda,22020640,,na
11/1/2025,Jodhpur,All_subzone,Roasted Chicken King Restaurant,19557504,,na
1/1/2026,Kota,All_subzone,Pheenix Cafe & Restaurant,20409752,,na
11/1/2025,Ajmer,All_subzone,Pani Puri Junction,21319262,,na
1/1/2026,Jodhpur,All_subzone,Mulla Ji Ka Dhaba,18959263,49,north indian
"""

# Uploads (override demo)
monthly_upload = st.file_uploader("Upload Monthly Portfolio CSV", type="csv")
res_upload = st.file_uploader("Upload Restaurant MoM CSV", type="csv")

# Load and clean monthly data
df_monthly = pd.read_csv(io.StringIO(monthly_data_str), header=None, index_col=0)
df_monthly = df_monthly.fillna(method='ffill', axis=0)  # Fill section names
df_monthly = df_monthly.transpose()
df_monthly.columns = [f"{section}_{metric}" if metric else section for section, metric in df_monthly.columns]
df_monthly = df_monthly.apply(pd.to_numeric, errors='coerce')

if monthly_upload:
    df_monthly = pd.read_csv(monthly_upload, header=None, index_col=0)
    df_monthly = df_monthly.fillna(method='ffill', axis=0)
    df_monthly = df_monthly.transpose()
    df_monthly.columns = [f"{section}_{metric}" if metric else section for section, metric in df_monthly.columns]
    df_monthly = df_monthly.apply(pd.to_numeric, errors='coerce')

# Load and clean restaurant data
df_res = pd.read_csv(io.StringIO(res_data_str))
df_res['Aggregation'] = pd.to_datetime(df_res['Aggregation'], format='%m/%d/%Y', errors='coerce')
df_res['Month'] = df_res['Aggregation'].dt.strftime('%Y-%m')
df_res['lvl'] = pd.to_numeric(df_res['lvl'], errors='coerce').fillna(0)

if res_upload:
    df_res = pd.read_csv(res_upload)
    df_res['Aggregation'] = pd.to_datetime(df_res['Aggregation'], format='%m/%d/%Y', errors='coerce')
    df_res['Month'] = df_res['Aggregation'].dt.strftime('%Y-%m')
    df_res['lvl'] = pd.to_numeric(df_res['lvl'], errors='coerce').fillna(0)

# Interactive Filters
col1, col2, col3 = st.columns(3)
with col1:
    selected_month = col1.selectbox("Select Month", df_monthly.index, index=len(df_monthly.index)-1)
with col2:
    selected_city = col2.selectbox("Select City", sorted(df_res['city_name'].unique()))
with col3:
    selected_cuisine = col3.selectbox("Select Cuisine", sorted(df_res['res_cuisine_new'].unique()))

# AI-Driven Insights (simple rule-based, expandable)
st.subheader("AI-Driven Insights")
gmv_change = df_monthly['Revenue_GMV'].pct_change().iloc[-1] * 100 if 'Revenue_GMV' in df_monthly.columns else 0
if gmv_change > 0:
    st.success(f"GMV grew {gmv_change:.1f}% MoM! Strong performance in ads and funnel.")
elif gmv_change < 0:
    st.warning(f"GMV declined {abs(gmv_change):.1f}% MoM. Check high ZVD ({df_monthly['Revenue_ZVD Discount %'].iloc[-1] if 'Revenue_ZVD Discount %' in df_monthly.columns else 'N/A'}) or low SL%.")
else:
    st.info("GMV stable MoM. Monitor customer segments.")

# Portfolio KPIs (Latest Month)
st.subheader("Portfolio Summary – Latest Month")
metrics = st.columns(5)
metrics[0].metric("Total Orders", f"{int(df_monthly['Orders_Total_OV'].iloc[-1] if 'Orders_Total_OV' in df_monthly.columns else 0):,}")
metrics[1].metric("GMV", f"₹{int(df_monthly['Revenue_GMV'].iloc[-1] if 'Revenue_GMV' in df_monthly.columns else 0):,}")
metrics[2].metric("AOV", f"₹{int(df_monthly['Revenue_AOV'].iloc[-1] if 'Revenue_AOV' in df_monthly.columns else 0):,}")
metrics[3].metric("Ads ROI", df_monthly['Advertisement_Ads ROI'].iloc[-1] if 'Advertisement_Ads ROI' in df_monthly.columns else "N/A")
metrics[4].metric("Organic Orders %", f"{df_monthly['Organic _Organic Orders%'].iloc[-1] if 'Organic _Organic Orders%' in df_monthly.columns else 'N/A'}")

# Charts Section
st.subheader("MoM Trends")
fig_orders = px.line(df_monthly[['Orders_Total_OV', 'Orders_Ads_ov']], title="Orders & Ads Orders Trend", markers=True)
fig_orders.update_layout(yaxis_title="Count")
st.plotly_chart(fig_orders, use_container_width=True)

fig_gmv = px.bar(df_monthly[['Revenue_GMV', 'Revenue_CV']], title="GMV & CV Trend", barmode='group')
fig_gmv.update_layout(yaxis_title="₹")
st.plotly_chart(fig_gmv, use_container_width=True)

fig_discounts = px.area(df_monthly[['Revenue_MVD Discount%', 'Revenue_Salt Discount %', 'Revenue_ZVD Discount %']], title="Discount Trends %")
st.plotly_chart(fig_discounts, use_container_width=True)

# Restaurant Table (Filtered & Interactive)
st.subheader(f"Restaurant MoM Details – {selected_month} | {selected_city} | {selected_cuisine}")
filtered_res = df_res[
    (df_res['Month'] == selected_month) &
    (df_res['city_name'] == selected_city) &
    (df_res['res_cuisine_new'] == selected_cuisine if selected_cuisine != "All" else True)
].sort_values('lvl', ascending=False)
st.dataframe(filtered_res[['res_name', 'lvl', 'res_cuisine_new', 'subzone', 'city_name']], use_container_width=True)

# Top Restaurants Chart
top_res_fig = px.bar(filtered_res.head(10), x='lvl', y='res_name', orientation='h', color='res_cuisine_new', title="Top 10 Restaurants by Orders (lvl)")
st.plotly_chart(top_res_fig, use_container_width=True)

# AI Query Chat (Basic pandas-based, add OpenAI for advanced)
st.subheader("Ask AI About the Data")
user_query = st.text_input("e.g., 'Top 5 cuisines in Jodhpur?' or 'Why did orders drop in March?'")
if user_query:
    if "top" in user_query.lower() and "cuisine" in user_query.lower():
        top_cuisines = df_res.groupby('res_cuisine_new')['lvl'].sum().nlargest(5)
        st.write(f"Top Cuisines: {top_cuisines.to_dict()}")
    elif "drop" in user_query.lower():
        st.write("Possible reasons: High discounts (ZVD up 4.82% in Mar) or funnel drop (M2O down to 13.43%). Check specific cities.")
    else:
        st.write("AI Response: Analyzing... (Add your OpenAI key for advanced queries)")

# Downloads
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button("📥 Download Monthly Report", df_monthly.to_csv().encode('utf-8'), "monthly_portfolio.csv")
with col_dl2:
    st.download_button("📥 Download Restaurant Report", df_res.to_csv(index=False).encode('utf-8'), "restaurant_mom.csv")

st.info("Demo mode with truncated data. Upload full CSVs above for accurate views. Contact for customizations!")
