# Show the most recent sales that either caused us to re-calculate currency
# values or had some meaninful conversion into chaos orbs (e.g. not generic
# items being sold for chaos)
select
	substr(sale.name, 1, 17) as `name`,
	substr(item.league, 1, 10) as `league`,
	sale.sale_amount as `$`,
	round(sale.sale_amount_chaos,2) as `$c`,
	substr(sale.sale_currency,1,15) as `currency`,
	round(sale.sale_amount_chaos/sale_amount,2) as `cur price`
from sale
	inner join item on sale.item_id = item.id
where
	(sale.is_currency = 1 or sale.sale_currency != 'Chaos Orb')
order by sale.id desc
limit 30;
