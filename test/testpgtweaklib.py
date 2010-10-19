# Copyright (c) 2010 Matt Harrison

import unittest

import pgtweaklib

class TestPgtweaklib(unittest.TestCase):
    def test_needs_mem_boost(self):
        results = """GroupAggregate  (cost=42856.20..45104.53 rows=32119 width=247) (actual time=32606.422..44289.146 rows=9869 loops=1)
   ->  Sort  (cost=42856.20..42936.50 rows=32119 width=247) (actual time=32605.346..43664.767 rows=162941 loops=1)
         Sort Key: nov_14_08ag_wk_vendor_fact.department, nov_14_08ag_wk_vendor_fact.department_name, nov_14_08ag_wk_vendor_fact.department_num, nov_14_08ag_wk_vendor_fact.category, nov_14_08ag_wk_vendor_fact.category_name, nov_14_08ag_wk_vendor_fact.category_num, nov_14_08ag_wk_vendor_fact.subcategory, nov_14_08ag_wk_vendor_fact.subcategory_name, nov_14_08ag_wk_vendor_fact.subcategory_num, nov_14_08ag_wk_vendor_fact.product, nov_14_08ag_wk_vendor_fact.primary_upc, nov_14_08ag_wk_vendor_fact.upc_description, nov_14_08ag_wk_vendor_fact.size, nov_14_08ag_wk_vendor_fact.create_date, nov_14_08ag_wk_vendor_fact.discontinued_date
         Sort Method:  external merge  Disk: 43768kB
         ->  Nested Loop  (cost=0.00..36717.41 rows=32119 width=247) (actual time=3.505..755.673 rows=162941 loops=1)
        """
        self.assertEquals(suggestions(results), 'up work_mem to at least 44MB')        
    
    def test_needs_index(self):
        """
        The following results should suggest adding an index
        """
        results = """                                                                                                                                                                                          QUERY PLAN                                                                                                                                                                                           
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Sort  (cost=2747.32..2747.32 rows=2 width=282) (actual time=774.035..774.087 rows=64 loops=1)
   Sort Key: product_dim.product, product_dim.subcategory_name, product_dim.category_num, product_dim.upc_description, product_dim.department_name, product_dim.subcategory_num, product_dim.discontinued_date, product_dim.manufacturer_code, product_dim.create_date, product_dim.size, product_dim.department_num, product_dim.primary_upc, product_dim.category_name, promo_dim.sales_type
   Sort Method:  quicksort  Memory: 58kB
   ->  HashAggregate  (cost=2747.24..2747.31 rows=2 width=282) (actual time=773.503..773.658 rows=64 loops=1)
         ->  Nested Loop  (cost=19.68..2747.10 rows=2 width=282) (actual time=0.866..762.048 rows=1538 loops=1)
               ->  Hash Join  (cost=19.68..2006.22 rows=219 width=73) (actual time=0.282..448.024 rows=57142 loops=1)
                     Hash Cond: (public.week_sales_fact.promo_key = promo_dim.promo_key)
                     ->  Hash Join  (cost=17.53..1998.67 rows=857 width=74) (actual time=0.133..318.213 rows=57142 loops=1)
                           Hash Cond: (public.week_sales_fact.week_key = week_dim.week_key)
                           ->  Append  (cost=0.00..1758.28 rows=57144 width=78) (actual time=0.008..189.884 rows=57142 loops=1)
                                 ->  Seq Scan on week_sales_fact  (cost=0.00..16.15 rows=2 width=154) (actual time=0.001..0.001 rows=0 loops=1)
                                       Filter: ((week_key >= 390) AND (week_key <= 393))
                                 ->  Seq Scan on week_sales_fact_390 week_sales_fact  (cost=0.00..428.90 rows=14060 width=78) (actual time=0.004..23.368 rows=14060 loops=1)
                                       Filter: ((week_key >= 390) AND (week_key <= 393))
                                 ->  Seq Scan on week_sales_fact_391 week_sales_fact  (cost=0.00..429.44 rows=14096 width=78) (actual time=0.009..24.123 rows=14096 loops=1)
                                       Filter: ((week_key >= 390) AND (week_key <= 393))
                                 ->  Seq Scan on week_sales_fact_392 week_sales_fact  (cost=0.00..443.19 rows=14546 width=78) (actual time=0.009..24.163 rows=14546 loops=1)
                                       Filter: ((week_key >= 390) AND (week_key <= 393))
                                 ->  Seq Scan on week_sales_fact_393 week_sales_fact  (cost=0.00..440.60 rows=14440 width=78) (actual time=0.010..24.430 rows=14440 loops=1)
                                       Filter: ((week_key >= 390) AND (week_key <= 393))
                           ->  Hash  (cost=17.49..17.49 rows=3 width=4) (actual time=0.115..0.115 rows=4 loops=1)
                                 ->  Seq Scan on week_dim  (cost=0.00..17.49 rows=3 width=4) (actual time=0.039..0.108 rows=4 loops=1)
                                       Filter: ((week_end >= '2009-10-20 00:00:00'::timestamp without time zone) AND (week_end <= '2009-11-10 00:00:00'::timestamp without time zone))
                     ->  Hash  (cost=1.51..1.51 rows=51 width=7) (actual time=0.140..0.140 rows=51 loops=1)
                           ->  Seq Scan on promo_dim  (cost=0.00..1.51 rows=51 width=7) (actual time=0.006..0.070 rows=51 loops=1)
               ->  Index Scan using product_dim_pkey on product_dim  (cost=0.00..3.37 rows=1 width=217) (actual time=0.003..0.003 rows=0 loops=57142)
                     Index Cond: (product_dim.product_key = public.week_sales_fact.product_key)
                     Filter: (((product_dim.category)::text = '   18 SOFT DRINKS'::text) AND ((product_dim.subcategory)::text = '   18     1 18-CSD SUGAR SOFT DRINKS'::text) AND ((product_dim.department)::text = '    1 GROCERY'::text))
 Total runtime: 774.359 ms
(29 rows)
"""
        query="""
EXPLAIN ANALYZE SELECT TIMESTAMP E'11/10/09' AS week_end, product_dim.category AS category, product_dim.category_num AS category_num, product_dim.category_name AS category_name, product_dim.product AS product, product_dim.primary_upc AS primary_upc, product_dim.upc_description AS upc_description, product_dim.size AS size, product_dim.create_date AS create_date, product_dim.discontinued_date AS discontinued_date, product_dim.manufacturer_code AS manufacturer_code, product_dim.subcategory_name AS subcategory_name, product_dim.subcategory AS subcategory, product_dim.subcategory_num AS subcategory_num, product_dim.subcategory_name AS subcategory_name, product_dim.category_num AS category_num, product_dim.upc_description AS upc_description, product_dim.department_name AS department_name, product_dim.subcategory_num AS subcategory_num, product_dim.discontinued_date AS discontinued_date, product_dim.manufacturer_code AS manufacturer_code, product_dim.department AS department, product_dim.department_num AS department_num, product_dim.department_name AS department_name, product_dim.create_date AS create_date, product_dim.size AS size, product_dim.department_num AS department_num, product_dim.primary_upc AS primary_upc, product_dim.category_name AS category_name, promo_dim.sales_type AS sales_type, sum(week_sales_fact.sales) AS sales, sum(week_sales_fact.sales_with_cost) AS sales_with_cost, sum(week_sales_fact.units) AS units, sum(week_sales_fact.units_with_cost) AS units_with_cost, sum(week_sales_fact.cost_with_cost) AS cost_with_cost, sum(week_sales_fact.dealamt) AS dealamt, sum(week_sales_fact.purbillback) AS purbillback, sum(week_sales_fact.scanbillback) AS scanbillback, sum(week_sales_fact.rebateamt) AS rebateamt, sum(week_sales_fact.regprice) AS regprice                                                                                       
         FROM product_dim, promo_dim, week_sales_fact, week_dim                                                               
         WHERE product_dim.department IN (E'    1 GROCERY') AND product_dim.category IN (E'   18 SOFT DRINKS') AND product_dim.subcategory IN (E'   18     1 18-CSD SUGAR SOFT DRINKS') AND week_dim.week_end BETWEEN E'10/20/09' AND E'11/10/09' AND week_sales_fact.product_key = product_dim.product_key AND week_sales_fact.promo_key = promo_dim.promo_key AND week_sales_fact.week_key = week_dim.week_key AND week_sales_fact.week_key BETWEEN 390 AND 393 GROUP BY product_dim.category, product_dim.category_num, product_dim.category_name, product_dim.product, product_dim.primary_upc, product_dim.upc_description, product_dim.size, product_dim.create_date, product_dim.discontinued_date, product_dim.manufacturer_code, product_dim.subcategory_name, product_dim.subcategory, product_dim.subcategory_num, product_dim.subcategory_name, product_dim.category_num, product_dim.upc_description, product_dim.department_name, product_dim.subcategory_num, product_dim.discontinued_date, product_dim.manufacturer_code, product_dim.department, product_dim.department_num, product_dim.department_name, product_dim.create_date, product_dim.size, product_dim.department_num, product_dim.primary_upc, product_dim.category_name, promo_dim.sales_type ORDER BY TIMESTAMP E'11/10/09', category, product, subcategory_name, subcategory, category_num, upc_description, department_name, subcategory_num, discontinued_date, manufacturer_code, department, create_date, size, department_num, primary_upc, category_name, sales_type                                                       ;
        """

        self.assertEquals(suggestions(results), 'add index to product_dim')


if __name__ == '__main__':
    unittest.main()
