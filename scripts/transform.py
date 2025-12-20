"""
Script de transformation des données Northwind
Nettoyage, enrichissement et préparation pour l'analyse
"""

import pandas as pd
import numpy as np
import os

class NorthwindTransformer:
    """Classe pour transformer les données extraites"""
    
    def __init__(self):
        self.raw_path = 'data/raw/'
        self.processed_path = 'data/processed/'
        
        # Créer le dossier de sortie
        os.makedirs(self.processed_path, exist_ok=True)
        
    def load_raw_data(self, filename):
        """Charge un fichier CSV depuis data/raw/"""
        try:
            df = pd.read_csv(f"{self.raw_path}{filename}")
            print(f"✓ Chargé: {filename} ({len(df)} lignes)")
            return df
        except Exception as e:
            print(f"✗ Erreur chargement {filename}: {e}")
            return None
    
    def clean_sales_data(self, df):
        """Nettoie et enrichit les données de ventes"""
        print("\n🧹 Nettoyage des données de ventes...")
        
        # Copie pour ne pas modifier l'original
        df_clean = df.copy()
        
        # 1. Convertir les dates
        date_columns = ['OrderDate', 'ShippedDate', 'PaidDate', 'SubmittedDate', 'CreationDate']
        for col in date_columns:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                except:
                    print(f"  ⚠ Impossible de convertir la colonne {col}")

        # Also parse invoice/due dates if present
        for col in ['InvoiceDate', 'DueDate']:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                except:
                    print(f"  ⚠ Impossible de convertir la colonne {col}")
        
        # 2. Extraire des composantes temporelles (si OrderDate existe)
        if 'OrderDate' in df_clean.columns:
            df_clean['Year'] = df_clean['OrderDate'].dt.year
            df_clean['Month'] = df_clean['OrderDate'].dt.month
            df_clean['Quarter'] = df_clean['OrderDate'].dt.quarter
            df_clean['DayOfWeek'] = df_clean['OrderDate'].dt.dayofweek
            df_clean['MonthName'] = df_clean['OrderDate'].dt.strftime('%B')
        
        # 3. Calculer le délai de livraison (si les dates existent)
        if 'ShippedDate' in df_clean.columns and 'OrderDate' in df_clean.columns:
            df_clean['DeliveryDays'] = (df_clean['ShippedDate'] - df_clean['OrderDate']).dt.days

        # Conserver un indicateur 'WasShipped' basé sur la présence initiale de ShippedDate
        # IMPORTANT: nous définissons ce flag AVANT d'appliquer les remplissages ultérieurs
        if 'ShippedDate' in df_clean.columns:
            df_clean['WasShipped'] = df_clean['ShippedDate'].notna()
        else:
            df_clean['WasShipped'] = False
        
        # 4. Créer des catégories de montant (si LineTotal existe)
        if 'LineTotal' in df_clean.columns:
            df_clean['AmountCategory'] = pd.cut(
                df_clean['LineTotal'],
                bins=[0, 100, 500, 1000, float('inf')],
                labels=['Petit', 'Moyen', 'Grand', 'Très Grand']
            )
        
        # 5. Gérer les valeurs manquantes
        missing_before = df_clean.isnull().sum().sum()
        
        # Remplir les valeurs numériques
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df_clean[col].isnull().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        
        # Remplir les valeurs catégorielles
        categorical_cols = df_clean.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df_clean[col].isnull().any():
                df_clean[col] = df_clean[col].fillna('Inconnu')
        
        missing_after = df_clean.isnull().sum().sum()

        # Additional targeted imputations for important columns
        # Notes: replace NaN with a clear placeholder so CSV -> DB keeps a value
        if 'Notes' in df_clean.columns:
            df_clean['Notes'] = df_clean['Notes'].fillna('Inconnu')

        # TaxStatus: if missing, infer from TaxRate (Taxable / Non-taxable)
        if 'TaxStatus' in df_clean.columns:
            if 'TaxRate' in df_clean.columns:
                df_clean['TaxStatus'] = df_clean['TaxStatus'].fillna(
                    df_clean['TaxRate'].apply(lambda x: 'Taxable' if pd.notnull(x) and x > 0 else 'Non-taxable')
                )
            else:
                df_clean['TaxStatus'] = df_clean['TaxStatus'].fillna('Unknown')

        # InvoiceDate: if missing, fallback to OrderDate
        if 'InvoiceDate' in df_clean.columns and 'OrderDate' in df_clean.columns:
            df_clean['InvoiceDate'] = df_clean['InvoiceDate'].fillna(df_clean['OrderDate'])

        # DueDate: if missing, try to infer from InvoiceDate, otherwise set to OrderDate + 30 days
        if 'DueDate' in df_clean.columns:
            if 'InvoiceDate' in df_clean.columns:
                df_clean['DueDate'] = df_clean['DueDate'].fillna(df_clean['InvoiceDate'] + pd.Timedelta(days=30))
            # second fallback: use OrderDate
            if 'OrderDate' in df_clean.columns:
                df_clean['DueDate'] = df_clean['DueDate'].fillna(df_clean['OrderDate'] + pd.Timedelta(days=30))

        # PaidDate: if missing, try InvoiceDate then DueDate then OrderDate + 30
        if 'PaidDate' in df_clean.columns:
            if 'InvoiceDate' in df_clean.columns:
                df_clean['PaidDate'] = df_clean['PaidDate'].fillna(df_clean['InvoiceDate'])
            if 'DueDate' in df_clean.columns:
                df_clean['PaidDate'] = df_clean['PaidDate'].fillna(df_clean['DueDate'])
            if 'OrderDate' in df_clean.columns:
                df_clean['PaidDate'] = df_clean['PaidDate'].fillna(df_clean['OrderDate'] + pd.Timedelta(days=30))

        # ShippedDate: if missing, fallback to OrderDate (assume 0 days delivery when unknown)
        if 'ShippedDate' in df_clean.columns and 'OrderDate' in df_clean.columns:
            df_clean['ShippedDate'] = df_clean['ShippedDate'].fillna(df_clean['OrderDate'])

        # Recompute DeliveryDays after imputations
        if 'ShippedDate' in df_clean.columns and 'OrderDate' in df_clean.columns:
            df_clean['DeliveryDays'] = (df_clean['ShippedDate'] - df_clean['OrderDate']).dt.days
        
        print(f"  • Dates converties")
        print(f"  • Composantes temporelles ajoutées")
        if 'DeliveryDays' in df_clean.columns:
            print(f"  • Délais de livraison calculés")
        print(f"  • Valeurs manquantes: {missing_before} → {missing_after}")
        
        return df_clean
    
    def create_aggregated_metrics(self, df):
        """Crée des métriques agrégées pour le dashboard"""
        print("\n📊 Création des métriques agrégées...")
        
        metrics = {}
        
        # 1. Ventes par mois (si les colonnes existent)
        if all(col in df.columns for col in ['Year', 'Month', 'LineTotal', 'OrderID', 'Quantity']):
            monthly_sales = df.groupby(['Year', 'Month']).agg({
                'LineTotal': 'sum',
                'OrderID': 'nunique',
                'Quantity': 'sum'
            }).reset_index()
            monthly_sales.columns = ['Year', 'Month', 'TotalSales', 'NumOrders', 'TotalQuantity']
            metrics['monthly_sales'] = monthly_sales
            print(f"  • Ventes mensuelles créées")
        
        # 2. Ventes par catégorie (si CategoryName existe)
        if 'CategoryName' in df.columns:
            category_sales = df.groupby('CategoryName').agg({
                'LineTotal': 'sum',
                'OrderID': 'nunique',
                'Quantity': 'sum'
            }).reset_index()
            category_sales.columns = ['Category', 'TotalSales', 'NumOrders', 'TotalQuantity']
            category_sales = category_sales.sort_values('TotalSales', ascending=False)
            metrics['category_sales'] = category_sales
            print(f"  • Ventes par catégorie créées")
        
        # 3. Top produits (si ProductName existe)
        if 'ProductName' in df.columns:
            product_sales = df.groupby('ProductName').agg({
                'LineTotal': 'sum',
                'Quantity': 'sum',
                'OrderID': 'nunique'
            }).reset_index()
            product_sales.columns = ['Product', 'TotalSales', 'Quantity', 'NumOrders']
            product_sales = product_sales.sort_values('TotalSales', ascending=False).head(20)
            metrics['top_products'] = product_sales
            print(f"  • Top produits créés")
        
        # 4. Ventes par pays (si CustomerCountry existe)
        if 'CustomerCountry' in df.columns:
            country_sales = df.groupby('CustomerCountry').agg({
                'LineTotal': 'sum',
                'OrderID': 'nunique',
                'CustomerID': 'nunique'
            }).reset_index()
            country_sales.columns = ['Country', 'TotalSales', 'NumOrders', 'NumCustomers']
            country_sales = country_sales.sort_values('TotalSales', ascending=False)
            metrics['country_sales'] = country_sales
            print(f"  • Ventes par pays créées")
        
        # 5. Performance des employés (si EmployeeName existe)
        if 'EmployeeName' in df.columns:
            employee_sales = df.groupby('EmployeeName').agg({
                'LineTotal': 'sum',
                'OrderID': 'nunique',
                'CustomerID': 'nunique'
            }).reset_index()
            employee_sales.columns = ['Employee', 'TotalSales', 'NumOrders', 'NumCustomers']
            employee_sales = employee_sales.sort_values('TotalSales', ascending=False)
            metrics['employee_sales'] = employee_sales
            print(f"  • Performance employés créée")
        
        # 6. KPIs globaux
        kpis = {}
        
        if 'LineTotal' in df.columns:
            kpis['TotalRevenue'] = df['LineTotal'].sum()
        
        if 'OrderID' in df.columns:
            kpis['TotalOrders'] = df['OrderID'].nunique()
        
        if 'CustomerID' in df.columns:
            kpis['TotalCustomers'] = df['CustomerID'].nunique()
        
        if 'ProductID' in df.columns:
            kpis['TotalProducts'] = df['ProductID'].nunique()
        
        if 'OrderID' in df.columns and 'LineTotal' in df.columns:
            order_totals = df.groupby('OrderID')['LineTotal'].sum()
            kpis['AvgOrderValue'] = order_totals.mean()
        
        if 'DeliveryDays' in df.columns:
            kpis['AvgDeliveryDays'] = df['DeliveryDays'].mean()
        
        metrics['kpis'] = pd.DataFrame([kpis])
        print(f"  • KPIs créés")
        
        print(f"  • Total: {len(metrics)} ensembles de métriques créés")
        
        return metrics
    
    def save_transformed_data(self, df, filename):
        """Sauvegarde les données transformées"""
        output_path = f"{self.processed_path}{filename}"
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✓ Sauvegardé: {output_path}")
    
    def transform_all(self):  # NOTE: This is the correct method name
        """Pipeline complet de transformation"""
        print("\n🚀 DÉBUT DE LA TRANSFORMATION\n")
        
        # 1. Charger les données brutes
        sales_df = self.load_raw_data('sales_analysis_complete.csv')
        if sales_df is None:
            print("✗ Impossible de charger les données")
            print("⚠ Essayez d'abord de charger sales_analysis.csv")
            sales_df = self.load_raw_data('sales_analysis.csv')
            if sales_df is None:
                print("✗ Aucune donnée disponible pour la transformation")
                return None, None
        
        # 2. Nettoyer et enrichir
        sales_clean = self.clean_sales_data(sales_df)
        
        # 3. Créer les métriques agrégées
        metrics = self.create_aggregated_metrics(sales_clean)
        
        # 4. Sauvegarder tout
        print("\n💾 Sauvegarde des données transformées...")
        self.save_transformed_data(sales_clean, 'sales_clean.csv')
        
        for key, df in metrics.items():
            self.save_transformed_data(df, f'{key}.csv')
        
        # 5. Résumé
        self.print_summary(sales_clean, metrics)
        
        print("\n✅ TRANSFORMATION TERMINÉE\n")
        
        return sales_clean, metrics
    
    def print_summary(self, df, metrics):
        """Affiche un résumé de la transformation"""
        print("\n" + "="*60)
        print("RÉSUMÉ DE LA TRANSFORMATION")
        print("="*60)
        
        print(f"\n📊 Données nettoyées:")
        print(f"  • Lignes: {len(df):,}")
        print(f"  • Colonnes: {len(df.columns)}")
        
        if 'OrderDate' in df.columns:
            print(f"  • Période: {df['OrderDate'].min()} à {df['OrderDate'].max()}")
        
        if 'kpis' in metrics:
            kpis = metrics['kpis'].iloc[0]
            print(f"\n💰 KPIs principaux:")
            
            if 'TotalRevenue' in kpis:
                print(f"  • Revenu total: ${kpis['TotalRevenue']:,.2f}")
            
            if 'TotalOrders' in kpis:
                print(f"  • Commandes: {int(kpis['TotalOrders']):,}")
            
            if 'TotalCustomers' in kpis:
                print(f"  • Clients: {int(kpis['TotalCustomers'])}")
            
            if 'AvgOrderValue' in kpis:
                print(f"  • Valeur moyenne commande: ${kpis['AvgOrderValue']:,.2f}")
            
            if 'AvgDeliveryDays' in kpis:
                print(f"  • Délai livraison moyen: {kpis['AvgDeliveryDays']:.1f} jours")
        
        print(f"\n📁 Fichiers générés dans {self.processed_path}:")
        if os.path.exists(self.processed_path):
            files = os.listdir(self.processed_path)
            for f in sorted(files):
                if f.endswith('.csv'):
                    print(f"  • {f}")
        
        print("="*60)


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("TRANSFORMATEUR DE DONNÉES NORTHWIND")
    print("="*60)
    
    transformer = NorthwindTransformer()
    
    try:
        sales_clean, metrics = transformer.transform_all()
        print("\n✓ Transformation terminée avec succès!")
        return sales_clean, metrics
    except Exception as e:
        print(f"\n✗ Erreur lors de la transformation: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    main()