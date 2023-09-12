import pandas as pd
import dash
import plotly.express as px
from dash import dcc ,html,dash_table
from dash.dependencies import Output,Input
import locale


locale.setlocale(locale.LC_ALL, 'es_PE.UTF-8')

#crear la aplicacion dash
app = dash.Dash(__name__)
# mportar o transformar la Data
df=pd.read_excel("C:\\Users\\luis\\Desktop\\saldos bancos.xlsx",sheet_name="Saldo de Moneda ",header=4)
df.iloc[0]=df.iloc[0].fillna("")
df.iloc[1]=df.iloc[1].fillna("")
df.columns=df.iloc[0].astype(str)+" "+df.iloc[1].astype(str)
df.drop(index=[0,1,14,15,16,17,18,21,30],inplace=True)
df1=df.reset_index(drop=True)
df2=df1.melt(id_vars=[df1.columns[0],df1.columns[1]],var_name="descripcion",value_name="valor")
df2[["fecha","descri"]]=df2["descripcion"].str.split(" ",n=1,expand=True)
df2.drop(columns=["descripcion"],inplace=True)
df2["fecha"]=df2["fecha"].replace("",pd.NA)
df2["fecha"].fillna(method="ffill",inplace=True)
df2["fecha"] = pd.to_datetime(df2["fecha"], format="%d/%m/%Y")
df2["Mes"]=df2["fecha"].dt.month_name(locale="es-ES.utf8")


app.layout=html.Div([
           html.H1("Reporte de Saldos Bancos"),
           
           # estos html.Div son para ordenar graficos y que esten en forma horizontal uno al lado de otra
           html.Div([            
           dcc.DatePickerSingle(id="picker",
                                date=df2["fecha"].min(),
                                display_format="DD/MM/YYYY",
                                placeholder='Selecciona una fecha',
                                style={"margin-left" :"20px","margin-top":"5px","width": "140px","font-size": "5px"}),
         
           # Dropdown para seleccionar moneda
           dcc.Dropdown(id="desplegable",
                        options=[{"label":"SOLES","value":"SOLES"},
                                 {"label":"DOLARES","value":"DOLARES"}],value="SOLES",
                        style={"margin-left": "10px", "margin-top": "5px","width": "150px"}),], style={'display': 'flex'}), # este ], style={'display': 'flex'}) es para que haga efecto
           
           # estos html.Div son para ordenar graficos y que esten en forma horizontal uno al lado de otra
           html.Div([
           # Gráfico de barras
           dcc.Graph(id="barra",
                    style={"margin-left":"20px","margin-top":"20px","width":"40%","height":"400px"}),
           
        
           
          # Tabla 
           html.Div(id='tabla1', className='table-container', style={'margin-top': '20px', 'margin-left': '90px','margin-right': '20px','height': '400px','width': '6%'}
                    ),
           
           
           # Nuevo gráfico de barras horizontal
           dcc.Graph(id="barra_horizontal",
           style={"margin-left":"250px","margin-top":"20px","width":"30%","height":"400px",'margin-right': '180px'}),],style={'display': 'flex'}),  # este ], style={'display': 'flex'}) es para que haga efecto
           
           
           
           
           # Tabla 
           html.Div(id='tabla2', className='table-container-2', style={'margin-top': '-60px','margin-left': '120px','width': '20%'}),                          
    
 ])
@app.callback(
            [Output("barra","figure"),
             Output("barra_horizontal","figure"),
             Output("tabla1","children"),
             Output("tabla2","children")],
            [Input("picker","date"),
             Input("desplegable","value")])

def visual( seleccion_date,seleccion_value):
   # Gráfico de barras
    dfx = df2.groupby([df2.columns[0], df2.columns[5], df2.columns[4]])[df2.columns[2]].sum().reset_index()
    dfx1=dfx[dfx["descri"]=="Saldo Bancos"]
    dfx2=dfx1[dfx1[" MONEDA"]==seleccion_value]    
    fig_bar = px.bar(dfx2, x='Mes', y='valor', title=f'Ingresos x Mes en {seleccion_value}')
    fig_bar.update_layout(autosize=False, width=500, height=300)
    
    # Eliminar los títulos de los ejes X e Y
    fig_bar.update_xaxes(title_text=None)
    fig_bar.update_yaxes(title_text=None)

    # Nuevo gráfico de barras horizontal
  
   
    dfy=df2[(df2["descri"]=="Saldo real")&(df2["fecha"]==seleccion_date)&(df2[" MONEDA"]==seleccion_value)].reset_index(drop=True)
    # Crear una columna formateada para las etiquetas en el eje X
    dfy['valor_formatted'] = dfy['valor'].apply(lambda x: f'{x:,.2f}')
   
    fig_bar_horizontal = px.bar(dfy, y='BANCOS ', x='valor', orientation='h', title=f'Saldo Real el {seleccion_date}')
    # Formatear las etiquetas en el eje X
    fig_bar_horizontal.update_traces(hovertemplate='%{x:,.2f}', selector=dict(type='bar'))

    fig_bar_horizontal.update_layout(autosize=False, width=500, height=500)   
    # Eliminar los títulos de los ejes X e Y
    fig_bar_horizontal.update_xaxes(title_text=None)
    fig_bar_horizontal.update_yaxes(title_text=None)

   
    # Tabla Saldo disponible por Banc0
    columns_to_show = ['BANCOS ', 'valor']  # Agrega aquí los nombres de las columnas que deseas mostrar
    dfy['valor'] = dfy['valor'].apply(lambda x: f'{x:,.2f}')  # Aplica formato de localización a una columna numérica
    
    sales_table = dash_table.DataTable(
      columns=[{'name': col, 'id': col} for col in columns_to_show],
      data=dfy[columns_to_show].to_dict('records'),
      style_table={'margin': '60px','margin-top': '40px'},
      style_header={
        'backgroundColor': 'lightblue',
        'fontWeight': 'bold',
        'textAlign': 'center',  # Centrar los títulos
        'color': 'darkblue'})  # Color del texto de los títulos
    
    
     # Tabla saldo disponible Empresa
    dfz=df2.groupby([df2.columns[0],df2.columns[3],df2.columns[4]])[df2.columns[2]].sum().reset_index()
    criterios = ["Saldo Bancos", "CH. No Cobrados", "No Disponible","Transf. Pendiente","Interb. Pendiente","Saldo real"]
    dfz1 = dfz[dfz["descri"].isin(criterios)].copy()
    # Crear una nueva columna para definir el orden de acuerdo a los criterios
    dfz1["orden"] = pd.Categorical(dfz1["descri"], categories=criterios, ordered=True)
    # Ordenar el DataFrame según la nueva columna "orden"
    dfz1 = dfz1.sort_values("orden")
    # Eliminar la columna de orden temporal
    dfz1.drop(columns=["orden"], inplace=True)
    dfz2= dfz1.reset_index(drop=True)
    dfz3=dfz1[(dfz1[" MONEDA"]==seleccion_value)&(dfz1["fecha"]==seleccion_date)].reset_index(drop=True)
    
    dfz3['valor'] = dfz3['valor'].apply(lambda x: f'{x:,.2f}')

    columns_show = ["descri", 'valor']  # Agrega aquí los nombres de las columnas que deseas mostrar
    other_table = dash_table.DataTable(
      columns=[{'name': col, 'id': col} for col in columns_show],
      data=dfz3[columns_show].to_dict('records'),
      style_table={'margin': '10px'},
      style_header={
        'backgroundColor': 'lightblue',
        'fontWeight': 'bold',
        'textAlign': 'center',  # Centrar los títulos
        'color': 'darkblue'})  # Color del texto de los títulos
    
    
    
    return fig_bar, fig_bar_horizontal, sales_table, other_table
    
 # Iniciar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True,port=8074)