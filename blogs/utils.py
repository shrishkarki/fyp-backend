from django.utils.text import slugify 

def unique_slug_generator(instance, new_slug = None): 
    if new_slug is not None: 
        slug = new_slug 
    else: 
        slug = slugify(instance.title) 
    Klass = instance.__class__ 
    qs_exists = Klass.objects.filter(slug = slug).exists() 
    if qs_exists: 
        new_slug = "{slug}-{blog_id}".format( 
            slug = slug, blog_id = instance.id) 
              
        return unique_slug_generator(instance, new_slug = new_slug) 
    return slug 