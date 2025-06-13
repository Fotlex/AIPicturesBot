from typing import List, Tuple
from django.db.models import Count
from project.database.models import Categories, Styles



async def get_paginated_main_menu_items(page: int, page_size: int) -> Tuple[List[Categories | Styles], bool]:
    start = (page - 1) * page_size
    end = page * page_size

    categories_query = Categories.objects.annotate(
        style_count=Count('styles')
    ).filter(style_count__gt=0).order_by('name')

    styles_without_category_query = Styles.objects.filter(category__isnull=True).order_by('name')
    
    items = ([item async for item in categories_query] + 
             [item async for item in styles_without_category_query])
    
    paginated_items = items[start:end]
    has_next_page = len(items) > end
    
    return paginated_items, has_next_page

async def get_paginated_styles_in_category(category_id: int, page: int, page_size: int) -> Tuple[List[Styles], bool, str]:
    start = (page - 1) * page_size
    end = page * page_size
    
    try:
        category = await Categories.objects.aget(id=category_id)
        category_name = category.name
    except Categories.DoesNotExist:
        return [], False, "Неизвестная категория"

    styles_query = Styles.objects.filter(category_id=category_id).order_by('name')
    
    total_styles = await styles_query.acount()
    
    paginated_styles = [style async for style in styles_query[start:end]]
    
    has_next_page = total_styles > end
    
    return paginated_styles, has_next_page, category_name