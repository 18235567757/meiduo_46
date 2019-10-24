def get_breadcrumb(category):

    beradcrumb = {
        'cat1':'',
        'cat2':'',
        'cat3':''
    }

    if category.parent is None:
        beradcrumb['cat1'] = category

    elif category.subs.count() == 0:

        # 三级
        beradcrumb['cat3'] = category
        beradcrumb['cat2'] = category.parent
        beradcrumb['cat1'] = category.parent.parent

    else:
        # 二级
        beradcrumb['cat2'] = category
        beradcrumb['cat3'] = category.parent


    return beradcrumb