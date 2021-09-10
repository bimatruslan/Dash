import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Div import Div
from dash_html_components.H5 import H5
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Style 

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

#import data
data = pd.ExcelFile('ikan.xlsx')
df_konsum = pd.read_excel(data, sheet_name= "AngkaKonsumsiIkan")
df_benih = pd.read_excel(data, sheet_name= "JumlahProduksiBenih")
df_budidaya = pd.read_excel(data, sheet_name= "PembudidayaIkan")
df_olahan = pd.read_excel(data, sheet_name= "ProdukOlahanIkan")
df_produksi = pd.read_excel(data, sheet_name= "ProduksiBudidayaNasional")
df_perlakuan = pd.read_excel(data, sheet_name= "ProduksiPerlakuanIkanNasional")

#Function untuk membuat bar plot dari rata-rata produksi ikan tiap daerah
def plot_produksi(data, ikan):
  pivot = pd.pivot_table(data, "Volume", index="NamaProvinsi", columns="NamaIkan",aggfunc="mean")
  pivot.sort_values(ikan, ascending= False, inplace=True)
  bar_chart = px.bar(pivot, x = pivot.index.get_level_values(0), y = ikan)
  bar_chart.update_layout(title = "Rata-rata Produksi "+ ikan+ " Tahun 2003- 2012",
                  xaxis_title = " ",
                  yaxis_title = " Volume"
                  )
  
  return bar_chart

# Plot Konsumsi
konsumsi = df_konsum[df_konsum["ParamKonsumsiIkan"].isin(["Penyediaan ikan untuk konsumsi per kapita",
                                                          "Konsumsi ikan per kapita"])]

konsumsi_plot = px.line(konsumsi, x= "Tahun", y= "Nilai", color="ParamKonsumsiIkan")
konsumsi_plot.update_layout(title = "Penyediaan Ikan dan Konsumsi Ikan per Kapita",
                  xaxis_title = "Tahun",
                  yaxis_title = "Kg/kapita"
                  )

#Plot Rata-rata pembudidaya
mean_provinsi = df_budidaya.groupby("NamaProvinsi").mean()
mean_provinsi.sort_values("Jumlah", ascending= False, inplace= True)
pembudidaya_plot = px.bar(mean_provinsi,x= mean_provinsi.index, y="Jumlah")
pembudidaya_plot.update_layout(title = "Rata-rata Pembudidaya Ikan per Provinsi (2002 - 2012)",
                  xaxis_title = " ",
                  yaxis_title = " "
                  )

pembudidaya_mean = pd.pivot_table(df_budidaya, values = "Jumlah", index = "Tahun", aggfunc="mean")

#Plot Trend Produksi komoditas per tahun
komoditas_per_tahun = pd.pivot_table(df_produksi,"Volume", index= "Tahun", columns = "Budidaya", aggfunc="mean")
komoditas_plot = px.line(komoditas_per_tahun, x= komoditas_per_tahun.index.get_level_values(0), y="semua budidaya")
komoditas_plot.update_layout(title="Rata-Rata Produksi Komoditas per Tahun",
                            xaxis_title= "Tahun",
                            yaxis_title = "Jumlah" )

#Plot Pie Chart Komoditas
komoditas_tertinggi = pd.pivot_table(df_produksi, "Volume", index = "NamaIkan", aggfunc="mean")
komoditas_tertinggi.drop(index=["total","rumput laut"],inplace = True)
komoditas_tertinggi.round()
pie_komoditas = px.pie(komoditas_tertinggi, values='Volume', names=komoditas_tertinggi.index.get_level_values(0),title='Persentase Komoditas')
pie_komoditas.update_traces(textposition='inside',textinfo='percent+label')


#Plot Donat Chart
komoditas_daerah = pd.pivot_table(df_produksi, "Volume", index="NamaProvinsi", columns="NamaIkan",aggfunc="mean")

def donut_chart(data, ikan_satu,ikan_dua,middle_satu,middle_dua, ukuran_font):
  
  specs = [[{'type':'domain'}, {'type':'domain'}]]

  plot = make_subplots(rows=1, cols=2, specs=specs)

  plot.add_trace(go.Pie(labels=data.index.get_level_values(0), values=data[ikan_satu], name=ikan_satu),
                1, 1)

  plot.add_trace(go.Pie(labels=data.index.get_level_values(0), values=data[ikan_dua], name=ikan_dua),
                1, 2)
  plot.update_traces(textposition='inside',hole=0.4, textinfo='percent+label')
  plot.update_layout(
      title_text="Daerah Produsen " + ikan_satu +" dan " +ikan_dua,
      # Add annotations in the center of the donut pies.
      annotations=[dict(text=ikan_satu, x=middle_satu, y=0.5, font_size=ukuran_font, showarrow=False),
                  dict(text=ikan_dua, x=middle_dua, y=0.5, font_size=ukuran_font, showarrow=False)
                  ]
                  )
  plot.update(layout_showlegend=False)
  return plot
  
#plot Scatter plot jumlah pembudidaya vs volume produksi
produk = df_budidaya.merge(df_produksi, how = "right", left_on=["NamaProvinsi", "Tahun"], right_on= ["NamaProvinsi","Tahun"])
produk.drop(columns = ["ID_y","ProvinsiID_y","Budidaya_y","Budidaya_x"], inplace= True)
produk.rename(columns = {"Jumlah" : "JumlahPembudidaya"}, inplace = True)
produk

scatter_plot = px.scatter(produk[(produk["Tahun"] == 2003) & (produk["NamaIkan"] == "total")], x="JumlahPembudidaya", y="Volume", trendline= "ols")
scatter_plot.update_layout(title = "Hubungan Jumlah Pembudidaya dengan Volume Produksi",
                  xaxis_title = "Jumlah Pembudidaya ",
                  yaxis_title = " Volume Produksi"
                  )



#Layout Dashboard
app.layout = html.Div(className="container-fluid",children=[
    html.Div(className="row",
    children=[
        html.Div(className="col align-self-center",children=
        [
            html.H2(
            "Dashboard Komoditas Ikan Nasional", style={'text-align': 'center'}
            )
        ]),
    ]),

    #Baris Card
    html.Div(className="row",
    children=[
        dbc.Card(className="col",children=[
            dbc.CardBody(
                [
                    html.Div([
                        html.H6("Rata-Rata Produksi Komoditas Tahun (2002-2012)",className='card-title', style={'text-align': 'center'} ),
                        html.H6(komoditas_per_tahun.mean().round(),className='card-text',style={'text-align': 'center'} )
                    ])
                ]
            )
        ],color="dark", inverse=True),
        dbc.Card(children=[
            dbc.CardBody(
                [
                    html.Div([
                        html.H6("Rata-Rata Pembudidaya Komoditas Tahun (2002-2012)",className='card-title', style={'text-align': 'center'} ),
                        html.H6(pembudidaya_mean.mean().round(),className='card-text',style={'text-align': 'center'} )
                    ])
                ]
            )
        ],className="col",color="dark", inverse=True),
    ]),

    #Baris Pertama
    html.Div(className="row",
    children=[
         html.Div(className="col",children=[
             dcc.Graph(id = "plot komoditas per tahun", figure= komoditas_plot)
        ]),
        
        html.Div(className="col",children=[
            dcc.Graph(id = "plot produksi", figure= konsumsi_plot)
        ])   
    ]),

    #Baris Kedua
    html.Div(className="row",
    children=[
        html.Div(className="col",children=
        [
            dcc.Graph(id="plot pembudidaya", figure= pembudidaya_plot)
        ])
    ]),

   #Baris ketiga
    html.Div(className= "row", 
    children=[
        html.Div(className="col",children=[
            dcc.Graph(id="plot pie chart komoditas",figure=pie_komoditas)
        ]),
        html.Div(className="col", children=[
            dcc.Graph(id="plot Scatter pembudidaya dan volume", figure=scatter_plot)
        ])
    ]),

    #Baris keempat
    html.Div(className="row",
     children=[
        html.Div(className="col",children=[
            dcc.Graph(id="plot donat chart bandeng udang", figure=donut_chart(komoditas_daerah,"bandeng","udang total",0.16,0.85,12) )
        ]),
        html.Div(className="col",children=[
            dcc.Graph(id="plot donat chart nila mas",figure=donut_chart(komoditas_daerah,"nila","mas",0.18,0.82,22))
        ])
    ])
])


# Main
if __name__ == '__main__':
    app.run_server(debug=True)