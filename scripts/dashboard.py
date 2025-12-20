"""
Tableau de bord analytique Northwind
Dashboard interactif avec Plotly et Dash
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input
import os

class NorthwindDashboard:
    """Classe pour créer le dashboard analytique"""
    
    def __init__(self):
        self.processed_path = 'data/processed/'
        self.figures_path = 'figures/'
        os.makedirs(self.figures_path, exist_ok=True)
        
        # Charger les données
        self.load_data()
        
    def load_data(self):
        """Charge toutes les données transformées"""
        print("📂 Chargement des données...")
        
        try:
            self.sales = pd.read_csv(f"{self.processed_path}sales_clean.csv")
            self.monthly = pd.read_csv(f"{self.processed_path}monthly_sales.csv")
            self.categories = pd.read_csv(f"{self.processed_path}category_sales.csv")
            self.products = pd.read_csv(f"{self.processed_path}top_products.csv")
            self.countries = pd.read_csv(f"{self.processed_path}country_sales.csv")
            self.employees = pd.read_csv(f"{self.processed_path}employee_sales.csv")
            self.kpis = pd.read_csv(f"{self.processed_path}kpis.csv")
            
            # Convertir les dates
            self.sales['OrderDate'] = pd.to_datetime(self.sales['OrderDate'])
            
            print("✓ Données chargées avec succès")
        except Exception as e:
            print(f"✗ Erreur: {e}")
    
    def load_all_data(self):
        """Charge TOUTES les données transformées"""
        print("📂 Chargement de TOUTES les données...")

        try:
            # Données principales
            self.sales = pd.read_csv(f"{self.processed_path}sales_enriched.csv")
            self.monthly = pd.read_csv(f"{self.processed_path}metrics_monthly_sales.csv")
            self.categories = pd.read_csv(f"{self.processed_path}metrics_category_sales.csv")
            self.countries = pd.read_csv(f"{self.processed_path}metrics_country_sales.csv")
            self.kpis = pd.read_csv(f"{self.processed_path}metrics_kpis_extended.csv")
            
            # Nouvelles données
            self.suppliers = pd.read_csv(f"{self.processed_path}metrics_supplier_by_products.csv")
            self.inventory = pd.read_csv(f"{self.processed_path}inventory_stock.csv")
            self.payments = pd.read_csv(f"{self.processed_path}metrics_payment_analysis.csv")
            self.shippers = pd.read_csv(f"{self.processed_path}metrics_shipper_performance.csv")
            
            # Convertir les dates
            if 'OrderDate' in self.sales.columns:
                self.sales['OrderDate'] = pd.to_datetime(self.sales['OrderDate'])
            
            print("✓ TOUTES les données chargées avec succès")
            print(f"  • Ventes: {len(self.sales):,} lignes")
            print(f"  • Fournisseurs: {len(self.suppliers)}")
            print(f"  • Produits en stock: {len(self.inventory)}")
            
        except Exception as e:
            print(f"✗ Erreur: {e}")

    def create_extended_kpi_cards(self):
        """Crée des cartes KPI étendues avec toutes les métriques"""
        if hasattr(self, 'kpis') and not self.kpis.empty:
            kpi = self.kpis.iloc[0]
            
            cards = html.Div([
                html.Div([
                    # Revenu et commandes
                    html.Div([
                        html.H3("💰 Revenu Total", style={'fontSize': '16px', 'color': '#666'}),
                        html.H2(f"${kpi.get('TotalRevenue', 0):,.0f}", style={'color': '#2ecc71', 'margin': '8px 0'}),
                        html.P(f"{kpi.get('TotalOrders', 0):,} commandes", style={'fontSize': '14px', 'color': '#888'})
                    ], style={'background': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'gridColumn': 'span 2'}),
                    
                    # Clients et produits
                    html.Div([
                        html.H3("👥 Clients", style={'fontSize': '16px', 'color': '#666'}),
                        html.H2(f"{int(kpi.get('TotalCustomers', 0)):,}", style={'color': '#3498db', 'margin': '8px 0'}),
                        html.P(f"{kpi.get('TotalProducts', 0):,} produits", style={'fontSize': '14px', 'color': '#888'})
                    ], style={'background': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    # Panier moyen
                    html.Div([
                        html.H3("📊 Panier Moyen", style={'fontSize': '16px', 'color': '#666'}),
                        html.H2(f"${kpi.get('AvgOrderValue', 0):,.0f}", style={'color': '#9b59b6', 'margin': '8px 0'}),
                        html.P(f"Max: ${kpi.get('MaxOrderValue', 0):,.0f}", style={'fontSize': '14px', 'color': '#888'})
                    ], style={'background': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    # Livraison
                    html.Div([
                        html.H3("🚚 Délai Livraison", style={'fontSize': '16px', 'color': '#666'}),
                        html.H2(f"{kpi.get('AvgDeliveryDays', 0):.1f} j", style={'color': '#e74c3c', 'margin': '8px 0'}),
                        html.P(f"Max: {kpi.get('MaxDeliveryDays', 0):.0f} j", style={'fontSize': '14px', 'color': '#888'})
                    ], style={'background': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    # Profit
                    html.Div([
                        html.H3("💹 Profit Total", style={'fontSize': '16px', 'color': '#666'}),
                        html.H2(f"${kpi.get('TotalProfit', 0):,.0f}", style={'color': '#f39c12', 'margin': '8px 0'}),
                        html.P(f"Marge: {kpi.get('AvgProfitMargin', 0):.1f}%", style={'fontSize': '14px', 'color': '#888'})
                    ], style={'background': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'gridColumn': 'span 2'}),
                    
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '15px', 'marginBottom': '30px'})
            ])
        
            return cards

        return html.Div("Aucune donnée disponible")

    def plot_supplier_analysis(self):
        """Graphique d'analyse des fournisseurs"""
        if not hasattr(self, 'suppliers') or self.suppliers.empty:
            return go.Figure()

        fig = go.Figure()

        # Barres pour le nombre de produits
        fig.add_trace(go.Bar(
            x=self.suppliers['SupplierCompany'],
            y=self.suppliers['ProductCount'],
            name='Nombre de produits',
            marker_color='#3498db',
            text=self.suppliers['ProductCount'],
            textposition='outside'
        ))

        # Ligne pour le prix moyen
        fig.add_trace(go.Scatter(
            x=self.suppliers['SupplierCompany'],
            y=self.suppliers['AvgPrice'],
            name='Prix moyen ($)',
            yaxis='y2',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title='🏭 Analyse des fournisseurs',
            xaxis_title='Fournisseur',
            yaxis_title='Nombre de produits',
            yaxis2=dict(
                title='Prix moyen ($)',
                overlaying='y',
                side='right'
            ),
            template='plotly_white',
            height=400,
            hovermode='x unified',
            legend=dict(x=1.1, y=1)
        )

        return fig

    def plot_inventory_analysis(self):
        """Graphique d'analyse de l'inventaire"""
        if not hasattr(self, 'inventory') or self.inventory.empty:
            return go.Figure()

        # Trier par valeur de stock
        inventory_sorted = self.inventory.sort_values('StockValue', ascending=False).head(15)

        fig = go.Figure()

        # Barres pour la valeur du stock
        fig.add_trace(go.Bar(
            name='Valeur du stock',
            x=inventory_sorted['ProductName'],
            y=inventory_sorted['StockValue'],
            marker_color=inventory_sorted['CurrentStock'],
            marker_colorscale='Viridis',
            text=inventory_sorted['StockValue'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Valeur: $%{y:,.0f}<br>Stock: %{marker.color}<extra></extra>'
        ))

        # Ligne pour le stock actuel (sur axe secondaire)
        fig.add_trace(go.Scatter(
            name='Stock actuel',
            x=inventory_sorted['ProductName'],
            y=inventory_sorted['CurrentStock'],
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title='📦 Top 15 produits par valeur de stock',
            xaxis_title='Produit',
            yaxis_title='Valeur du stock ($)',
            yaxis2=dict(
                title='Stock actuel (unités)',
                overlaying='y',
                side='right'
            ),
            template='plotly_white',
            height=400,
            hovermode='x unified',
            xaxis={'categoryorder': 'total descending'},
            legend=dict(x=1.1, y=1)
        )

        return fig

    def plot_payment_analysis(self):
        """Graphique d'analyse des paiements"""
        if not hasattr(self, 'payments') or self.payments.empty:
            return go.Figure()

        fig = go.Figure()

        # Diagramme en barres groupées
        fig.add_trace(go.Bar(
            name='Nombre de commandes',
            x=self.payments['PaymentType'],
            y=self.payments['NumOrders'],
            marker_color='#3498db',
            text=self.payments['NumOrders'],
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            name='Montant total',
            x=self.payments['PaymentType'],
            y=self.payments['TotalSales'],
            marker_color='#2ecc71',
            text=self.payments['TotalSales'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside',
            yaxis='y2'
        ))

        fig.update_layout(
            title='💳 Analyse des méthodes de paiement',
            xaxis_title='Type de paiement',
            yaxis_title='Nombre de commandes',
            yaxis2=dict(
                title='Montant total ($)',
                overlaying='y',
                side='right'
            ),
            template='plotly_white',
            height=400,
            barmode='group',
            hovermode='x unified'
        )

        return fig

    def plot_shipper_performance(self):
        """Graphique de performance des transporteurs"""
        if not hasattr(self, 'shippers') or self.shippers.empty:
            return go.Figure()

        fig = go.Figure()

        # Graphique à bulles
        fig.add_trace(go.Scatter(
            x=self.shippers['NumOrders'],
            y=self.shippers['AvgDeliveryDays'],
            mode='markers',
            marker=dict(
                size=self.shippers['TotalSales'] / 1000,  # Taille proportionnelle au chiffre d'affaires
                color=self.shippers['TotalShippingFees'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Frais de livraison ($)')
            ),
            text=self.shippers['Shipper'] + '<br>' +
                    'Commandes: ' + self.shippers['NumOrders'].astype(str) + '<br>' +
                    'Délai moyen: ' + self.shippers['AvgDeliveryDays'].round(1).astype(str) + ' jours<br>' +
                    'CA: $' + self.shippers['TotalSales'].round(0).astype(str),
            hoverinfo='text'
        ))

        fig.update_layout(
            title='🚚 Performance des transporteurs',
            xaxis_title='Nombre de commandes',
            yaxis_title='Délai de livraison moyen (jours)',
            template='plotly_white',
            height=400,
            hovermode='closest'
        )

        return fig

    def create_dash_app_extended(self):
        """Crée l'application Dash interactive COMPLÈTE"""
        app = Dash(__name__)

        app.layout = html.Div([
            # En-tête
            html.Div([
                html.H1('📊 Tableau de Bord Analytique Northwind - COMPLET', 
                        style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
                html.P('Analyse complète des ventes, inventaire, fournisseurs et transporteurs',
                        style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '20px'}),
                html.Hr(),
            ]),
            
            # KPIs étendus
            self.create_extended_kpi_cards(),
            
            # Section 1: Ventes
            html.Div([
                html.H2('📈 Analyse des Ventes', style={'color': '#2c3e50', 'marginBottom': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=self.plot_monthly_sales())
                    ], style={'width': '50%'}),
                    
                    html.Div([
                        dcc.Graph(figure=self.plot_category_distribution())
                    ], style={'width': '50%'}),
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
                
                html.Div([
                    html.Div([
                        dcc.Graph(figure=self.plot_top_products())
                    ], style={'width': '50%'}),
                    
                    html.Div([
                        dcc.Graph(figure=self.plot_delivery_3d())
                    ], style={'width': '50%'}),
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
            ]),
            
            # Section 2: Opérations
            html.Div([
                html.H2('🏭 Analyse Opérationnelle', style={'color': '#2c3e50', 'marginBottom': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=self.plot_supplier_analysis())
                    ], style={'width': '50%'}),
                    
                    html.Div([
                        dcc.Graph(figure=self.plot_inventory_analysis())
                    ], style={'width': '50%'}),
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
                
                html.Div([
                    html.Div([
                        dcc.Graph(figure=self.plot_payment_analysis())
                    ], style={'width': '50%'}),
                    
                    html.Div([
                        dcc.Graph(figure=self.plot_shipper_performance())
                    ], style={'width': '50%'}),
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
            ]),
            
            # Section 3: Performance employés
            html.Div([
                html.H2('👔 Performance des Employés', style={'color': '#2c3e50', 'marginBottom': '20px'}),
                dcc.Graph(figure=self.plot_employee_performance())
            ]),
            
            # Pied de page
            html.Footer([
                html.Hr(),
                html.P('Dashboard Northwind Complet | Analyse de toutes les données Excel | Projet BI 2025',
                        style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '30px', 'padding': '20px'})
            ])
            
        ], style={'padding': '30px', 'fontFamily': 'Arial, sans-serif', 'background': '#ecf0f1', 'maxWidth': '1400px', 'margin': '0 auto'})

        return app

    def create_kpi_cards(self):
        """Crée les cartes KPI"""
        kpi = self.kpis.iloc[0]
        
        cards = html.Div([
            html.Div([
                html.Div([
                    html.H3("💰 Revenu Total", style={'fontSize': '18px', 'color': '#666'}),
                    html.H2(f"${kpi['TotalRevenue']:,.0f}", style={'color': '#2ecc71', 'margin': '10px 0'}),
                ], style={'background': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H3("📦 Commandes", style={'fontSize': '18px', 'color': '#666'}),
                    html.H2(f"{int(kpi['TotalOrders']):,}", style={'color': '#3498db', 'margin': '10px 0'}),
                ], style={'background': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H3("👥 Clients", style={'fontSize': '18px', 'color': '#666'}),
                    html.H2(f"{int(kpi['TotalCustomers'])}", style={'color': '#e74c3c', 'margin': '10px 0'}),
                ], style={'background': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H3("📊 Panier Moyen", style={'fontSize': '18px', 'color': '#666'}),
                    html.H2(f"${kpi['AvgOrderValue']:,.0f}", style={'color': '#9b59b6', 'margin': '10px 0'}),
                ], style={'background': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '20px', 'marginBottom': '30px'})
        ])
        
        return cards
    
    def plot_monthly_sales(self):
        """Graphique des ventes mensuelles"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.monthly.index,
            y=self.monthly['TotalSales'],
            mode='lines+markers',
            name='Ventes',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        
        fig.update_layout(
            title='📈 Évolution des ventes mensuelles',
            xaxis_title='Mois',
            yaxis_title='Ventes ($)',
            template='plotly_white',
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_category_distribution(self):
        """Graphique des ventes par catégorie"""
        fig = px.pie(
            self.categories,
            values='TotalSales',
            names='Category',
            title='🎯 Répartition des ventes par catégorie',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    
    def plot_top_products(self):
        """Top 10 produits"""
        top10 = self.products.head(10)
        
        fig = go.Figure(go.Bar(
            x=top10['TotalSales'],
            y=top10['Product'],
            orientation='h',
            marker=dict(
                color=top10['TotalSales'],
                colorscale='Viridis',
                showscale=True
            ),
            text=top10['TotalSales'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='🏆 Top 10 Produits',
            xaxis_title='Ventes ($)',
            yaxis_title='',
            template='plotly_white',
            height=400,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def plot_country_sales(self):
        """Ventes par pays"""
        top_countries = self.countries.head(15)
        
        fig = px.bar(
            top_countries,
            x='Country',
            y='TotalSales',
            title='🌍 Ventes par pays (Top 15)',
            color='TotalSales',
            color_continuous_scale='Blues',
            text='TotalSales'
        )
        
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis={'categoryorder': 'total descending'}
        )
        
        return fig

    def plot_delivery_3d(self):
        """3D vertical bars: X=OrderDate, Y=EmployeeName (categorical), Z=Orders count.

        Shows two series (Delivered, Not Delivered). Each vertical bar is drawn as a thin line from Z=0 to Z=Orders
        and a marker at the bar top. Hover shows sample customers involved for that point.
        """
        if not hasattr(self, 'sales') or self.sales.empty:
            return go.Figure()

        df = self.sales.copy()

        # Ensure date column
        if 'OrderDate' in df.columns:
            df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
        else:
            # fallback to Year/Month (first day of month)
            if 'OrderYear' in df.columns and 'OrderMonth' in df.columns:
                df['OrderDate'] = pd.to_datetime(df['OrderYear'].astype(str) + '-' + df['OrderMonth'].astype(str) + '-01', errors='coerce')
            else:
                df['OrderDate'] = pd.to_datetime(df.get('OrderDate', None), errors='coerce')

        # Delivered flag: prefer explicit 'WasShipped' set during transform; otherwise fall back to ShippedDate
        if 'WasShipped' in df.columns:
            # 'WasShipped' was computed BEFORE any ShippedDate imputations in the transformer
            df['Delivered'] = df['WasShipped'].astype(bool)
        else:
            df['Delivered'] = False
            if 'ShippedDate' in df.columns:
                df['ShippedDate'] = pd.to_datetime(df['ShippedDate'], errors='coerce')
                df.loc[df['ShippedDate'].notna(), 'Delivered'] = True

        # StatusName can override and mark as delivered when applicable
        if 'StatusName' in df.columns:
            delivered_status = df['StatusName'].astype(str).str.lower().isin(['shipped', 'delivered', 'closed'])
            df.loc[delivered_status, 'Delivered'] = True

        # Ensure names exist
        df['EmployeeName'] = df.get('EmployeeName', df.get('Employee', 'Unknown'))
        df['CustomerName'] = df.get('CustomerName', df.get('CustomerCompany', df.get('Customer', 'Unknown')))

        # Aggregate by date + employee + delivered flag
        if 'OrderID' in df.columns:
            agg = df.groupby([df['OrderDate'].dt.date, 'EmployeeName', 'Delivered']).agg(
                Orders=('OrderID', 'nunique'),
                Customers=('CustomerName', lambda s: ', '.join(sorted(s.dropna().unique())[:3]))
            ).reset_index()
        else:
            agg = df.groupby([df['OrderDate'].dt.date, 'EmployeeName', 'Delivered']).agg(
                Orders=('CustomerName', 'size'),
                Customers=('CustomerName', lambda s: ', '.join(sorted(s.dropna().unique())[:3]))
            ).reset_index()

        if agg.empty:
            return go.Figure()

        # Map employees to numeric positions
        employees = sorted(agg['EmployeeName'].unique())
        emp_map = {e: i for i, e in enumerate(employees)}
        agg['y'] = agg['EmployeeName'].map(emp_map)

        fig = go.Figure()

        # Build traces per delivered flag; draw vertical line segments and marker at top
        for delivered_flag, name, color in [(True, 'Delivered', '#2ecc71'), (False, 'Not Delivered', '#e74c3c')]:
            sub = agg[agg['Delivered'] == delivered_flag].sort_values(['OrderDate', 'EmployeeName'])
            if sub.empty:
                continue

            # Prepare line segments (x,x,None), (y,y,None), (0,orders,None)
            x_lines, y_lines, z_lines = [], [], []
            x_marks, y_marks, z_marks, texts = [], [], [], []

            for _, row in sub.iterrows():
                date_val = pd.to_datetime(row['OrderDate'])
                y_val = row['y']
                orders = int(row['Orders'])
                customers_sample = row.get('Customers', '')

                x_lines.extend([date_val, date_val, None])
                y_lines.extend([y_val, y_val, None])
                z_lines.extend([0, orders, None])

                x_marks.append(date_val)
                y_marks.append(y_val)
                z_marks.append(orders)
                texts.append(f"Date: {date_val.date()}<br>Employee: {row['EmployeeName']}<br>Orders: {orders}<br>Customers: {customers_sample}")

            # Thin vertical lines
            fig.add_trace(go.Scatter3d(
                x=x_lines,
                y=y_lines,
                z=z_lines,
                mode='lines',
                line=dict(color=color, width=6),
                hoverinfo='none',
                showlegend=False
            ))

            # Markers at tops
            customdata = list(zip(sub['EmployeeName'].values, sub['Customers'].values))
            # Use z as orders count
            fig.add_trace(go.Scatter3d(
                x=x_marks,
                y=y_marks,
                z=z_marks,
                mode='markers',
                marker=dict(size=[max(6, min(6 + int(v), 30)) for v in z_marks], color=color, opacity=0.9),
                name=name,
                customdata=customdata,
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Employee: %{customdata[0]}<br>Orders: %{z}<br>Customers: %{customdata[1]}<extra></extra>'
            ))

        # Add a small annotation when there are no non-delivered orders
        total_delivered = int(agg[agg['Delivered'] == True]['Orders'].sum()) if 'Delivered' in agg.columns else 0
        total_not_delivered = int(agg[agg['Delivered'] == False]['Orders'].sum()) if 'Delivered' in agg.columns else 0

        if total_not_delivered == 0:
            # Suggest re-running transform to preserve WasShipped if you expect non-delivered orders
            note = "No non-delivered orders found. If you expect undelivered orders, re-run `scripts/transform.py` to update 'WasShipped' flag."
            fig.add_annotation(xref='paper', yref='paper', x=0.02, y=0.95,
                               text=note, showarrow=False, align='left', bgcolor='lightyellow', bordercolor='gray')

        fig.update_layout(
            title='📦 Commandes livrées vs non-livrées (3D - Orders count)',
            template='plotly_white',
            height=600,
            scene=dict(
                xaxis=dict(title='Order Date', type='date'),
                yaxis=dict(title='Employee', tickmode='array', tickvals=list(emp_map.values()), ticktext=list(emp_map.keys())),
                zaxis=dict(title='Orders', type='linear')
            ),
            legend=dict(x=0.85, y=0.95)
        )

        return fig
        fig.update_layout(
            title='📦 Commandes livrées vs non-livrées (3D)',
            template='plotly_white',
            height=600,
            scene=dict(
                xaxis=dict(title='Order Date', type='date'),
                yaxis=dict(title='Employee', tickmode='array', tickvals=list(emp_map.values()), ticktext=list(emp_map.keys())),
                zaxis=dict(title='Customer', tickmode='array', tickvals=list(cust_map.values()), ticktext=list(cust_map.keys()))
            ),
            legend=dict(x=0.85, y=0.95)
        )

        return fig
    
    def plot_employee_performance(self):
        """Performance des employés"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Ventes',
            x=self.employees['Employee'],
            y=self.employees['TotalSales'],
            marker_color='#3498db'
        ))
        
        fig.add_trace(go.Bar(
            name='Nombre de commandes',
            x=self.employees['Employee'],
            y=self.employees['NumOrders'] * 100,  # Échelle pour visualisation
            marker_color='#e74c3c'
        ))
        
        fig.update_layout(
            title='👔 Performance des employés',
            xaxis_title='Employé',
            yaxis_title='Ventes ($)',
            template='plotly_white',
            height=400,
            barmode='group'
        )
        
        return fig
    
    def create_dash_app(self):
        """Crée l'application Dash interactive"""
        app = Dash(__name__)
        
        app.layout = html.Div([
            html.Div([
                html.H1('📊 Tableau de Bord Analytique Northwind', 
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
                html.Hr(),
            ]),
            
            # KPIs
            self.create_kpi_cards(),
            
            # Graphiques principaux
            html.Div([
                html.Div([
                    dcc.Graph(figure=self.plot_monthly_sales())
                ], style={'width': '50%'}),
                
                html.Div([
                    dcc.Graph(figure=self.plot_category_distribution())
                ], style={'width': '50%'}),
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=self.plot_top_products())
                ], style={'width': '50%'}),
                
                html.Div([
                    dcc.Graph(figure=self.plot_delivery_3d())
                ], style={'width': '50%'}),
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
            
            html.Div([
                dcc.Graph(figure=self.plot_employee_performance())
            ]),
            
            html.Footer([
                html.Hr(),
                html.P('Dashboard créé avec Python, Plotly et Dash | Projet BI Northwind 2025',
                      style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '30px'})
            ])
            
        ], style={'padding': '30px', 'fontFamily': 'Arial, sans-serif', 'background': '#ecf0f1'})
        
        return app
    
    def save_static_charts(self):
        """Sauvegarde les graphiques en PNG"""
        print("\n💾 Sauvegarde des graphiques...")
        
        charts = {
            'monthly_sales.png': self.plot_monthly_sales(),
            'category_distribution.png': self.plot_category_distribution(),
            'top_products.png': self.plot_top_products(),
            'delivery_3d.png': self.plot_delivery_3d(),
            'employee_performance.png': self.plot_employee_performance()
        }
        
        for filename, fig in charts.items():
            path = f"{self.figures_path}{filename}"
            fig.write_image(path, width=1200, height=600)
            print(f"  ✓ {filename}")
        
        print(f"\n📁 Graphiques sauvegardés dans {self.figures_path}")
    
    def run(self, debug=True, port=8050):
        """Lance le dashboard interactif"""
        print("\n🚀 Lancement du dashboard...")
        print(f"📡 Serveur démarré sur http://localhost:{port}")
        print("💡 Appuyez sur Ctrl+C pour arrêter\n")
        
        app = self.create_dash_app()
        # When `debug=True`, Flask's reloader spawns a child process which
        # can cause the module-level startup code to run twice. Disable the
        # reloader here to avoid the dashboard launching two times during
        # local development. If you need the reloader, run with
        # `use_reloader=True` explicitly.
        app.run(debug=debug, port=port, use_reloader=False)


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("CRÉATION DU TABLEAU DE BORD NORTHWIND")
    print("="*60 + "\n")
    
    # Créer le dashboard
    dashboard = NorthwindDashboard()
    
    # Sauvegarder les graphiques statiques
    # dashboard.save_static_charts()  # Décommenter si plotly-kaleido est installé
    
    # Lancer le dashboard interactif - CORRECTED LINE
    dashboard.run(debug=True, port=8080)


if __name__ == "__main__":
    main()