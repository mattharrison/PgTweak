import unittest
from pgtweaklib import tree


BASIC = """                                     QUERY PLAN                                     
------------------------------------------------------------------------------------                                 
 Result  (cost=0.00..0.01 rows=1 width=0) (actual time=0.003..0.004 rows=1 loops=1)                                  
 Total runtime: 0.025 ms                                                                                             
(2 rows)"""

STAR = """                                                                                                                                                                                          QUERY PLAN                                                                                                                                                                                           
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
class TestNode(unittest.TestCase):
    def test_basic(self):
        root = tree.build_tree(BASIC)
        self.assertEquals(root.name, "Result")

    def test_star(self):
        root = tree.build_tree(STAR)
        self.assertEquals(root.name, 'Sort')
        hash_agg = root.children[0]
        self.assertEquals(len(root.children), 1)
        self.assertEquals(hash_agg.name, 'HashAggregate')
        self.assertEquals([x.name for x in hash_agg.children], ['Nested Loop'])
        parent = hash_agg.children[0]
        for names in [ ['Hash Join', 'Index Scan'], ['Hash Join', 'Hash'],['Append', 'Hash'], ['Seq Scan', 'Seq Scan', 'Seq Scan', 'Seq Scan', 'Seq Scan', ]]:
            self.assertEquals([x.name for x in parent.children], names)
            parent = parent.children[0]
        nest_loop = hash_agg.children[0]
if __name__ == '__main__':
    unittest.main()
