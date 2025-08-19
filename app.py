from shiny import App,render,ui,reactive
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shinywidgets import render_plotly
import faicons
import matplotlib.ticker as mticker
import calendar
df1=pd.read_excel('Superstore.xlsx',index_col=0,parse_dates=['Order Date','Ship Date'])
df1.columns=df1.columns.str.replace(' ', '_', regex=True)
df1 = df1.dropna(subset=["Order_Date","Sales"])  


app_ui=ui.page_fluid(
   
    ui.layout_sidebar(
        ui.sidebar(ui.card(ui.row(ui.output_image("logo",height="100px"),
        
        ui.h3("Filters",style="text-align:center;"),
        ui.input_selectize("Month",'Select Month',choices=["All"]+df1["Order_Date"].dt.month_name().sort_values(ascending=True).unique().tolist(),multiple=True,selected=["All"]),
        ui.input_selectize('Year',"Select Year",choices=["All"]+df1["Order_Date"].dt.year.sort_values(ascending=True).unique().tolist(),multiple=True,selected=["All"]),
        
    ))),
    
    ui.div(
        ui.h1("Superstore Sales Analysis", style="text-align:center; margin-bottom:60px;font-weight:bold;"),
        ui.output_ui("kpi"),
        
        ui.layout_columns(
        
        ui.card(ui.row(
        ui.card(ui.output_ui("discount"),class_="bg-info"),
        ui.card_header("Top Product Categories",style="text-allign:center;"),
        

        ui.card(ui.output_data_frame("table"),width="50%",class_="bg-info")),
        ),
        ui.card(ui.output_plot("sec"),height="400px",width="100px",class_="bg-info"),

        ui.card(ui.output_plot("one"),height="400px",width="100px",class_="bg-info"),
        
        ),
        ui.layout_columns(
        ui.card(ui.output_plot("pie"),title="Sales by Region",width=3,class_="bg-info"),

        ui.card(ui.output_plot("bar"),width=3,class_="bg-info"),
        ui.card(ui.output_plot("customers"),width=3,class_="bg-info"),
       
        ),
        ui.card(ui.output_plot("line"))
        ),style="background-color:lightgrey;"

    
    
    ))
def server(input,output,session):
    @reactive.Calc
    def filtered_df():
        df=df1.copy()
        years=input.Year() or[]
        months=input.Month() or []
        if months and "All" not in input.Month() and years and "All"  not in input.Year():
            years=[int(y) for y in years if y.isdigit()]
            df=df[(df['Order_Date'].dt.month_name().isin(months))&(df['Order_Date'].dt.year.isin(years))]
        elif years and "All" not in input.Year():
           years=[int(y) for y in years if y.isdigit()]
           return df[df['Order_Date'].dt.year.isin(years)]
        elif months and "All" not in input.Month():

            return df[df['Order_Date'].dt.month_name().isin(months)]
        
        return df
        
     
    @output
    @render.text
    def title():
        df=filtered_df()
        ui.output_text("Filters")
    @output
    @render.image
    def logo():
        img={"src": "cart.png","style":"border-radius:50%; margin:5px;paddind:0;display;block"}
        return img

    @output  
    @render.ui
    def kpi():
        df=filtered_df()
        total_sales=df['Sales'].sum()
        total_orders=df['Order_ID'].unique()
        total_profit=df['Profit'].sum()
        ftotal_orders=f"{len(total_orders):,}"
        ftotal_sales=f"{total_sales:,.2f}"
        ftotal_profit=f"{total_profit:,.2f}"
        return ui.div(
            ui.layout_columns(
            ui.card(ui.value_box(ui.tags.b('Total Orders'),ftotal_orders,showcase=faicons.icon_svg("credit-card",height="40px",fill="lightblue"),showcase_layout="top right",height="130px",style="background: linear-gradient(to right, #2980B9, #6DD5FA, #FFFFFF); border-radius:12px; color:white;"
,)),
            ui.card(ui.value_box(ui.tags.b('Total Sales'),ftotal_sales,showcase=faicons.icon_svg("money-bill",height="40px",fill="lightblue"),showcase_layout="top right",height="10px",theme="bg-gradient-blue-lightblue",style="background: linear-gradient(to right, #2980B9, #6DD5FA, #FFFFFF); border-radius:12px; color:white;"
)),
            ui.card(ui.value_box(ui.tags.b('Total Profit'),ftotal_profit,showcase=faicons.icon_svg("piggy-bank",height="40px",fill="lightblue"),showcase_layout="top right",height="100px",style="background: linear-gradient(to right, #2980B9, #6DD5FA, #FFFFFF); border-radius:12px; color:white;"
)),style="background-color:lightgrey;border-radius:10px;")
        )
    
   
    @output
    @render.plot
    def sec():
        df=filtered_df()
        fig,ax=plt.subplots()
        dt=df['Segment'].value_counts()
        wedges,texts,autotexts=ax.pie(dt, autopct='%1.1f%%', radius=1.0,startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
        fig.suptitle("Buyer Segmentation")
        plt.ylabel('')
        plt.setp(autotexts, size=10, weight="bold",)
        plt.setp(texts, size=10, weight="bold")
        ax.set_xlabel('')
        fig.subplots_adjust(top=0.6, bottom=0.1, )
        ax.legend(wedges, dt.index, loc='best',fontsize=6, title="Segments")
        fig.patch.set_facecolor('#0dcaf0')
        return fig
        plt.tight_layout()

    @output
    @render.data_frame
    def table():
        df=filtered_df()
        df3=df.groupby("Category")["Order_ID"].count().reset_index()
        df3.columns=["Category","Total Orders"]
        return render.DataTable(
            df3,height="155px"
           )
    @output
    @render.text
    def discount():
        df=filtered_df()
        avgdiscount=f"{df['Discount'].mean()*100:.2f} %"
        return ui.value_box(ui.tags.b("Average Discount"),avgdiscount,showcase=faicons.icon_svg("percent",height="50px",fill='lightblue'),showcase_layout="top right",height="100px",class_="bg-light",style="background: linear-gradient(to right, #2980B9, #6DD5FA, #FFFFFF); border-radius:12px; color:white;")
        
     


    @output
    @render.plot
    def one():
        df=filtered_df()

        fig,ax=plt.subplots(figsize=(6, 4))
        gd=df.groupby('City')['Order_ID'].count().sort_values(ascending=False).head(5).reset_index()
        #gd.plot(kind='barh',x='City',ax=ax,color='skyblue')
        ax.barh(gd['City'], gd['Order_ID'], color='blue')
        max_val=gd['Order_ID'].max()
        ax.invert_yaxis()
        ax.grid(axis='x',linestyle='--', alpha=0.4)
        fig.set_facecolor('#0dcaf0')
    
        ax.set_xticks(range(0,max_val +200,200))
        ax.tick_params(axis='x',rotation=45)
        for spine in ax.spines.values():
            spine.set_visible(False)
        plt.title("Top 5 Cities by Orders")
        return fig
    @output
    @render.plot
    def pie():
        df=filtered_df()
        fig,ax=plt.subplots(figsize=(7,6))
        dat=df.groupby("Region")['Sales'].sum()
        wedges,texts,autotexts=ax.pie(dat,autopct='%1.1f%%', radius=1.2,labels=None,startangle=90,wedgeprops=dict(width=0.4,edgecolor='white'),colors=['#ff9999','#66b3ff','#99ff99', '#ffcc99'])
        fig.suptitle("Regional Sales")
        fig.subplots_adjust(top=0.58,bottom=0.1)
        ax.set_ylabel('')
        ax.set_xlabel('')
        plt.setp(autotexts, size=10, weight="bold")
        plt.setp(texts, size=10, weight="bold")
        ax.legend(wedges,dat.index,loc='best',fontsize=6, title="Regions")
        fig.patch.set_facecolor('#0dcaf0')
        return fig
    @output
    @render.plot
    def bar():
        df=filtered_df()
        plt.figure(figsize=(8, 5) )
        grdf=df.groupby('State')['Sales'].sum().sort_values(ascending=False).head(5).reset_index()
        fig,ax=plt.subplots()
        ax.bar(grdf['State'],grdf['Sales'],color='blue')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

        fig.patch.set_facecolor('#0dcaf0')
        plt.xticks(grdf['State'],rotation=45)
        plt.suptitle("Top 5 states by Sales")
        
        return fig
        
    @output
    @render.plot
    def customers():
        df=filtered_df()
        fillt=df.groupby("Customer_Name")["Sales"].sum().sort_values(ascending=False).head(5).reset_index()
        plt.figure(figsize=(8,5))
        fig,ax=plt.subplots()
        ax.barh(fillt["Customer_Name"],fillt["Sales"],color="blue")
        ax.grid(True,linestyle="--",alpha=0.4)
        plt.suptitle("Top 5 customers by sales")
        fig.patch.set_facecolor('#0dcaf0')
        ax.invert_yaxis()
        return fig




    @output
    @render.plot
    def line():
        df4=filtered_df()
        df4["Order_Date"] = pd.to_datetime(df4["Order_Date"], errors="coerce")
        df4['Month']=df4["Order_Date"].dt.month_name()
        grdf2=df4.groupby('Month')['Sales'].sum().reset_index()

        month_order=list(calendar.month_name[1:])
        df4["Month"]=pd.Categorical(df4["Month"],categories=month_order,ordered=True)
        grdf2=df4.groupby('Month')['Sales'].sum().reset_index()
        grdf2=grdf2.sort_values("Month")
        plt.figure(figsize=(4,3))
        fig,ax=plt.subplots()
        ax.plot(grdf2["Month"],grdf2["Sales"],marker='o')
        ax.set_title("Monthly Sales")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.grid(True, linestyle='--', alpha=0.4)
        fig.patch.set_facecolor('#0dcaf0')
        plt.tight_layout()
        ax.tick_params(axis="y",labelsize=10)
        plt.xticks(grdf2["Month"],rotation=45,ha="right")
        plt.tight_layout()
        return fig
app=App(app_ui,server)