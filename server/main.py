#!/usr/bin/env python3
"""
E-commerce Sales Data Analytics MCP Server
Provides intelligent querying capabilities for sales data analysis
"""

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
from pathlib import Path
import logging

# MCP Server imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcommerceMCPServer:
    def __init__(self):
        self.server = Server("ecommerce-analytics")
        self.db_path = "ecommerce_data.db"
        self.data_loaded = False
        self.setup_server()
    
    def setup_server(self):
        """Setup MCP server with tools and resources"""
        
        # Register tools
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="sales_overview",
                    description="Get overall sales performance metrics and KPIs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date_range": {
                                "type": "string",
                                "description": "Date range filter (e.g., 'last_30_days', 'this_month', 'this_year')",
                                "default": "all"
                            }
                        }
                    }
                ),
                Tool(
                    name="product_analysis",
                    description="Analyze product performance, top sellers, and inventory insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "enum": ["top_products", "category_performance", "inventory_status", "profit_analysis"],
                                "description": "Type of product analysis to perform"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["analysis_type"]
                    }
                ),
                Tool(
                    name="customer_insights",
                    description="Analyze customer behavior, segments, and lifetime value",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "insight_type": {
                                "type": "string",
                                "enum": ["top_customers", "geographic_distribution", "purchase_patterns", "customer_lifetime_value"],
                                "description": "Type of customer analysis"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["insight_type"]
                    }
                ),
                Tool(
                    name="sales_trends",
                    description="Analyze sales trends over time, seasonality, and forecasting",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "trend_type": {
                                "type": "string",
                                "enum": ["monthly_trends", "daily_patterns", "seasonal_analysis", "growth_rate"],
                                "description": "Type of trend analysis"
                            },
                            "period": {
                                "type": "string",
                                "description": "Time period for analysis",
                                "default": "all"
                            }
                        },
                        "required": ["trend_type"]
                    }
                ),
                Tool(
                    name="custom_query",
                    description="Execute custom SQL-like queries on the sales data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query_description": {
                                "type": "string",
                                "description": "Natural language description of what you want to analyze"
                            },
                            "filters": {
                                "type": "object",
                                "description": "Optional filters (date_range, category, region, etc.)",
                                "default": {}
                            }
                        },
                        "required": ["query_description"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if not self.data_loaded:
                    await self.load_data()
                
                if name == "sales_overview":
                    result = await self.get_sales_overview(arguments.get("date_range", "all"))
                elif name == "product_analysis":
                    result = await self.analyze_products(
                        arguments["analysis_type"], 
                        arguments.get("limit", 10)
                    )
                elif name == "customer_insights":
                    result = await self.analyze_customers(
                        arguments["insight_type"],
                        arguments.get("limit", 10)
                    )
                elif name == "sales_trends":
                    result = await self.analyze_trends(
                        arguments["trend_type"],
                        arguments.get("period", "all")
                    )
                elif name == "custom_query":
                    result = await self.execute_custom_query(
                        arguments["query_description"],
                        arguments.get("filters", {})
                    )
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def load_data(self):
        """Load and process the e-commerce data"""
        try:
            # Initialize database
            conn = sqlite3.connect(self.db_path)
            
            # Sample data structure based on typical e-commerce datasets
            # You would replace this with actual CSV loading from Kaggle
            sample_data = self.generate_sample_data()
            
            # Create tables and load data
            for table_name, df in sample_data.items():
                df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            conn.close()
            self.data_loaded = True
            logger.info("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def generate_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Generate sample e-commerce data (replace with actual CSV loading)"""
        np.random.seed(42)
        
        # Generate sample orders data
        n_orders = 5000
        orders_data = {
            'order_id': [f'ORD-{i:06d}' for i in range(1, n_orders + 1)],
            'customer_id': [f'CUST-{np.random.randint(1, 1000):04d}' for _ in range(n_orders)],
            'order_date': pd.date_range('2023-01-01', '2024-12-31', periods=n_orders),
            'total_amount': np.random.lognormal(4, 0.5, n_orders).round(2),
            'status': np.random.choice(['completed', 'cancelled', 'pending'], n_orders, p=[0.85, 0.10, 0.05]),
            'shipping_state': np.random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH'], n_orders),
            'payment_method': np.random.choice(['credit_card', 'paypal', 'debit_card'], n_orders, p=[0.6, 0.25, 0.15])
        }
        orders_df = pd.DataFrame(orders_data)
        
        # Generate sample products data
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Beauty']
        n_products = 500
        products_data = {
            'product_id': [f'PROD-{i:04d}' for i in range(1, n_products + 1)],
            'product_name': [f'Product {i}' for i in range(1, n_products + 1)],
            'category': np.random.choice(categories, n_products),
            'price': np.random.uniform(10, 500, n_products).round(2),
            'cost': np.random.uniform(5, 250, n_products).round(2),
            'stock_quantity': np.random.randint(0, 1000, n_products)
        }
        products_df = pd.DataFrame(products_data)
        products_df['profit_margin'] = ((products_df['price'] - products_df['cost']) / products_df['price'] * 100).round(2)
        
        # Generate sample order items data
        n_order_items = 8000
        order_items_data = {
            'order_item_id': range(1, n_order_items + 1),
            'order_id': np.random.choice(orders_df['order_id'], n_order_items),
            'product_id': np.random.choice(products_df['product_id'], n_order_items),
            'quantity': np.random.randint(1, 5, n_order_items),
            'unit_price': np.random.uniform(10, 500, n_order_items).round(2)
        }
        order_items_df = pd.DataFrame(order_items_data)
        order_items_df['total_price'] = (order_items_df['quantity'] * order_items_df['unit_price']).round(2)
        
        # Generate sample customers data
        customer_ids = orders_df['customer_id'].unique()
        customers_data = {
            'customer_id': customer_ids,
            'customer_name': [f'Customer {i}' for i in range(len(customer_ids))],
            'email': [f'customer{i}@email.com' for i in range(len(customer_ids))],
            'registration_date': pd.date_range('2022-01-01', '2024-01-01', periods=len(customer_ids)),
            'customer_segment': np.random.choice(['Premium', 'Regular', 'Budget'], len(customer_ids), p=[0.2, 0.6, 0.2])
        }
        customers_df = pd.DataFrame(customers_data)
        
        return {
            'orders': orders_df,
            'products': products_df,
            'order_items': order_items_df,
            'customers': customers_df
        }

    async def get_sales_overview(self, date_range: str) -> Dict[str, Any]:
        """Get overall sales performance metrics"""
        conn = sqlite3.connect(self.db_path)
        
        # Build date filter
        date_filter = self.build_date_filter(date_range)
        
        # Total sales
        total_sales_query = f"""
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM orders 
        WHERE status = 'completed' {date_filter}
        """
        
        sales_metrics = pd.read_sql_query(total_sales_query, conn)
        
        # Sales by status
        status_query = f"""
        SELECT status, COUNT(*) as count, SUM(total_amount) as revenue
        FROM orders {('WHERE ' + date_filter.replace('AND ', '')) if date_filter else ''}
        GROUP BY status
        """
        
        status_breakdown = pd.read_sql_query(status_query, conn)
        
        # Top states by sales
        state_query = f"""
        SELECT shipping_state, COUNT(*) as orders, SUM(total_amount) as revenue
        FROM orders 
        WHERE status = 'completed' {date_filter}
        GROUP BY shipping_state
        ORDER BY revenue DESC
        LIMIT 5
        """
        
        top_states = pd.read_sql_query(state_query, conn)
        
        conn.close()
        
        return {
            "period": date_range,
            "summary_metrics": sales_metrics.to_dict('records')[0],
            "status_breakdown": status_breakdown.to_dict('records'),
            "top_states": top_states.to_dict('records'),
            "insights": self.generate_sales_insights(sales_metrics.iloc[0])
        }

    async def analyze_products(self, analysis_type: str, limit: int) -> Dict[str, Any]:
        """Analyze product performance"""
        conn = sqlite3.connect(self.db_path)
        
        if analysis_type == "top_products":
            query = """
            SELECT 
                p.product_name,
                p.category,
                SUM(oi.quantity) as units_sold,
                SUM(oi.total_price) as total_revenue,
                AVG(oi.unit_price) as avg_price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'completed'
            GROUP BY p.product_id, p.product_name, p.category
            ORDER BY total_revenue DESC
            LIMIT ?
            """
            
        elif analysis_type == "category_performance":
            query = """
            SELECT 
                p.category,
                COUNT(DISTINCT p.product_id) as product_count,
                SUM(oi.quantity) as total_units_sold,
                SUM(oi.total_price) as total_revenue,
                AVG(p.profit_margin) as avg_profit_margin
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
            GROUP BY p.category
            ORDER BY total_revenue DESC
            LIMIT ?
            """
            
        elif analysis_type == "inventory_status":
            query = """
            SELECT 
                product_id,
                product_name,
                category,
                stock_quantity,
                price,
                CASE 
                    WHEN stock_quantity = 0 THEN 'Out of Stock'
                    WHEN stock_quantity < 50 THEN 'Low Stock'
                    WHEN stock_quantity < 100 THEN 'Medium Stock'
                    ELSE 'High Stock'
                END as stock_status
            FROM products
            ORDER BY stock_quantity ASC
            LIMIT ?
            """
            
        elif analysis_type == "profit_analysis":
            query = """
            SELECT 
                p.product_name,
                p.category,
                p.price,
                p.cost,
                p.profit_margin,
                COALESCE(SUM(oi.quantity), 0) as units_sold,
                COALESCE(SUM(oi.total_price), 0) as revenue,
                COALESCE(SUM(oi.quantity * p.cost), 0) as total_cost,
                COALESCE(SUM(oi.total_price) - SUM(oi.quantity * p.cost), 0) as total_profit
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
            GROUP BY p.product_id
            ORDER BY total_profit DESC
            LIMIT ?
            """
        
        results = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        
        return {
            "analysis_type": analysis_type,
            "results": results.to_dict('records'),
            "insights": self.generate_product_insights(analysis_type, results)
        }

    async def analyze_customers(self, insight_type: str, limit: int) -> Dict[str, Any]:
        """Analyze customer behavior and segments"""
        conn = sqlite3.connect(self.db_path)
        
        if insight_type == "top_customers":
            query = """
            SELECT 
                c.customer_id,
                c.customer_segment,
                COUNT(o.order_id) as total_orders,
                SUM(o.total_amount) as total_spent,
                AVG(o.total_amount) as avg_order_value,
                MAX(o.order_date) as last_order_date
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.status = 'completed'
            GROUP BY c.customer_id
            ORDER BY total_spent DESC
            LIMIT ?
            """
            
        elif insight_type == "geographic_distribution":
            query = """
            SELECT 
                shipping_state,
                COUNT(DISTINCT customer_id) as unique_customers,
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value
            FROM orders
            WHERE status = 'completed'
            GROUP BY shipping_state
            ORDER BY total_revenue DESC
            LIMIT ?
            """
            
        elif insight_type == "purchase_patterns":
            query = """
            SELECT 
                CASE 
                    WHEN COUNT(o.order_id) = 1 THEN 'One-time Buyer'
                    WHEN COUNT(o.order_id) BETWEEN 2 AND 5 THEN 'Occasional Buyer'
                    WHEN COUNT(o.order_id) BETWEEN 6 AND 10 THEN 'Regular Buyer'
                    ELSE 'Frequent Buyer'
                END as customer_type,
                COUNT(DISTINCT c.customer_id) as customer_count,
                AVG(SUM(o.total_amount)) as avg_customer_value
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.status = 'completed'
            GROUP BY c.customer_id
            HAVING COUNT(o.order_id) > 0
            GROUP BY customer_type
            ORDER BY avg_customer_value DESC
            """
            
        elif insight_type == "customer_lifetime_value":
            query = """
            SELECT 
                c.customer_segment,
                COUNT(DISTINCT c.customer_id) as customer_count,
                AVG(customer_stats.total_spent) as avg_lifetime_value,
                AVG(customer_stats.total_orders) as avg_orders_per_customer,
                AVG(customer_stats.days_active) as avg_customer_lifespan_days
            FROM customers c
            JOIN (
                SELECT 
                    customer_id,
                    SUM(total_amount) as total_spent,
                    COUNT(*) as total_orders,
                    JULIANDAY(MAX(order_date)) - JULIANDAY(MIN(order_date)) as days_active
                FROM orders
                WHERE status = 'completed'
                GROUP BY customer_id
            ) customer_stats ON c.customer_id = customer_stats.customer_id
            GROUP BY c.customer_segment
            ORDER BY avg_lifetime_value DESC
            """
        
        results = pd.read_sql_query(query, conn, params=[limit] if insight_type != "customer_lifetime_value" and insight_type != "purchase_patterns" else [])
        conn.close()
        
        return {
            "insight_type": insight_type,
            "results": results.to_dict('records'),
            "insights": self.generate_customer_insights(insight_type, results)
        }

    async def analyze_trends(self, trend_type: str, period: str) -> Dict[str, Any]:
        """Analyze sales trends over time"""
        conn = sqlite3.connect(self.db_path)
        
        if trend_type == "monthly_trends":
            query = """
            SELECT 
                strftime('%Y-%m', order_date) as month,
                COUNT(*) as orders,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_order_value,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM orders
            WHERE status = 'completed'
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month
            """
            
        elif trend_type == "daily_patterns":
            query = """
            SELECT 
                CASE cast(strftime('%w', order_date) as integer)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_of_week,
                COUNT(*) as orders,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_order_value
            FROM orders
            WHERE status = 'completed'
            GROUP BY strftime('%w', order_date)
            ORDER BY cast(strftime('%w', order_date) as integer)
            """
            
        elif trend_type == "seasonal_analysis":
            query = """
            SELECT 
                CASE cast(strftime('%m', order_date) as integer)
                    WHEN 12 OR cast(strftime('%m', order_date) as integer) IN (1,2) THEN 'Winter'
                    WHEN cast(strftime('%m', order_date) as integer) IN (3,4,5) THEN 'Spring'
                    WHEN cast(strftime('%m', order_date) as integer) IN (6,7,8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(*) as orders,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_order_value
            FROM orders
            WHERE status = 'completed'
            GROUP BY season
            ORDER BY revenue DESC
            """
            
        elif trend_type == "growth_rate":
            query = """
            WITH monthly_sales AS (
                SELECT 
                    strftime('%Y-%m', order_date) as month,
                    SUM(total_amount) as revenue
                FROM orders
                WHERE status = 'completed'
                GROUP BY strftime('%Y-%m', order_date)
                ORDER BY month
            ),
            growth_calc AS (
                SELECT 
                    month,
                    revenue,
                    LAG(revenue) OVER (ORDER BY month) as prev_month_revenue
                FROM monthly_sales
            )
            SELECT 
                month,
                revenue,
                prev_month_revenue,
                CASE 
                    WHEN prev_month_revenue IS NOT NULL THEN 
                        ROUND(((revenue - prev_month_revenue) / prev_month_revenue * 100), 2)
                    ELSE NULL
                END as growth_rate_percent
            FROM growth_calc
            ORDER BY month
            """
        
        results = pd.read_sql_query(query, conn)
        conn.close()
        
        return {
            "trend_type": trend_type,
            "period": period,
            "results": results.to_dict('records'),
            "insights": self.generate_trend_insights(trend_type, results)
        }

    async def execute_custom_query(self, query_description: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom analysis based on natural language description"""
        # This is a simplified implementation - in practice, you'd use NLP to convert
        # natural language to SQL queries
        
        conn = sqlite3.connect(self.db_path)
        
        # Simple keyword-based query mapping
        query_lower = query_description.lower()
        
        if "revenue" in query_lower and "by category" in query_lower:
            query = """
            SELECT 
                p.category,
                SUM(oi.total_price) as revenue,
                COUNT(DISTINCT o.order_id) as orders
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'completed'
            GROUP BY p.category
            ORDER BY revenue DESC
            """
        elif "top selling" in query_lower:
            query = """
            SELECT 
                p.product_name,
                SUM(oi.quantity) as units_sold,
                SUM(oi.total_price) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'completed'
            GROUP BY p.product_id, p.product_name
            ORDER BY units_sold DESC
            LIMIT 10
            """
        else:
            # Default query - sales overview
            query = """
            SELECT 
                'Total Orders' as metric,
                COUNT(*) as value
            FROM orders
            WHERE status = 'completed'
            UNION ALL
            SELECT 
                'Total Revenue' as metric,
                ROUND(SUM(total_amount), 2) as value
            FROM orders
            WHERE status = 'completed'
            """
        
        results = pd.read_sql_query(query, conn)
        conn.close()
        
        return {
            "query_description": query_description,
            "filters_applied": filters,
            "results": results.to_dict('records'),
            "interpretation": f"Analysis for: {query_description}"
        }

    def build_date_filter(self, date_range: str) -> str:
        """Build SQL date filter based on date range"""
        if date_range == "all":
            return ""
        elif date_range == "last_30_days":
            return "AND order_date >= date('now', '-30 days')"
        elif date_range == "this_month":
            return "AND strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')"
        elif date_range == "this_year":
            return "AND strftime('%Y', order_date) = strftime('%Y', 'now')"
        else:
            return ""

    def generate_sales_insights(self, metrics: pd.Series) -> List[str]:
        """Generate insights from sales metrics"""
        insights = []
        
        avg_order = metrics['avg_order_value']
        if avg_order > 100:
            insights.append(f"Strong average order value of ${avg_order:.2f} indicates healthy customer spending")
        elif avg_order < 50:
            insights.append(f"Lower average order value of ${avg_order:.2f} suggests opportunity for upselling")
        
        total_orders = metrics['total_orders']
        unique_customers = metrics['unique_customers']
        repeat_rate = (total_orders - unique_customers) / unique_customers * 100 if unique_customers > 0 else 0
        
        if repeat_rate > 50:
            insights.append(f"High customer retention with {repeat_rate:.1f}% repeat purchase rate")
        elif repeat_rate < 20:
            insights.append(f"Low repeat purchase rate of {repeat_rate:.1f}% indicates need for customer retention strategies")
        
        return insights

    def generate_product_insights(self, analysis_type: str, results: pd.DataFrame) -> List[str]:
        """Generate insights from product analysis"""
        insights = []
        
        if analysis_type == "top_products" and not results.empty:
            top_product = results.iloc[0]
            insights.append(f"Top product '{top_product['product_name']}' generated ${top_product['total_revenue']:,.2f} in revenue")
            
        elif analysis_type == "category_performance" and not results.empty:
            top_category = results.iloc[0]
            insights.append(f"'{top_category['category']}' is the leading category with ${top_category['total_revenue']:,.2f} in sales")
            
        elif analysis_type == "inventory_status":
            out_of_stock = len(results[results['stock_status'] == 'Out of Stock'])
            low_stock = len(results[results['stock_status'] == 'Low Stock'])
            if out_of_stock > 0:
                insights.append(f"{out_of_stock} products are out of stock - immediate restocking needed")
            if low_stock > 0:
                insights.append(f"{low_stock} products have low inventory - consider restocking soon")
        
        return insights

    def generate_customer_insights(self, insight_type: str, results: pd.DataFrame) -> List[str]:
        """Generate insights from customer analysis"""
        insights = []
        
        if insight_type == "top_customers" and not results.empty:
            top_customer_spend = results.iloc[0]['total_spent']
            insights.append(f"Top customer has spent ${top_customer_spend:,.2f} - consider VIP treatment")
            
        elif insight_type == "customer_lifetime_value" and not results.empty:
            premium_clv = results[results['customer_segment'] == 'Premium']['avg_lifetime_value'].iloc[0] if len(results[results['customer_segment'] == 'Premium']) > 0 else 0
            regular_clv = results[results['customer_segment'] == 'Regular']['avg_lifetime_value'].iloc[0] if len(results[results['customer_segment'] == 'Regular']) > 0 else 0
            if premium_clv > regular_clv * 2:
                insights.append(f"Premium customers have {premium_clv/regular_clv:.1f}x higher lifetime value - focus on premium acquisition")
        
        return insights

    def generate_trend_insights(self, trend_type: str, results: pd.DataFrame) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []
        
        if trend_type == "growth_rate" and not results.empty:
            recent_growth = results.iloc[-1]['growth_rate_percent'] if results.iloc[-1]['growth_rate_percent'] is not None else 0
            if recent_growth > 10:
                insights.append(f"Strong growth of {recent_growth}% in the latest period")
            elif recent_growth < -10:
                insights.append(f"Concerning decline of {abs(recent_growth)}% in the latest period - investigation needed")
                
        elif trend_type == "daily_patterns" and not results.empty:
            best_day = results.loc[results['revenue'].idxmax(), 'day_of_week']
            worst_day = results.loc[results['revenue'].idxmin(), 'day_of_week']
            insights.append(f"{best_day} is the strongest sales day, while {worst_day} is the weakest")
        
        return insights

async def main():
    """Main function to run the MCP server"""
    server_instance = EcommerceMCPServer()
    
    # Initialize the server
    options = InitializationOptions(
        server_name="ecommerce-analytics",
        server_version="1.0.0"
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())