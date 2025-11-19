"""
Social sharing utilities for products and projects
"""
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote


def get_absolute_url(request, path):
    """Get absolute URL for sharing"""
    if hasattr(settings, 'SITE_URL'):
        base_url = settings.SITE_URL
    else:
        scheme = 'https' if request.is_secure() else 'http'
        base_url = f"{scheme}://{request.get_host()}"
    return f"{base_url}{path}"


def get_product_share_url(request, product):
    """Get shareable URL for a product"""
    path = reverse('product_detail', kwargs={'slug': product.slug})
    return get_absolute_url(request, path)


def get_project_share_url(request, project):
    """Get shareable URL for a project"""
    path = reverse('project_detail', kwargs={'slug': project.slug})
    return get_absolute_url(request, path)


def get_vendor_share_url(request, vendor):
    """Get shareable URL for a vendor"""
    path = reverse('vendor_profile_public', kwargs={'vendor_id': vendor.id})
    return get_absolute_url(request, path)


def get_facebook_share_url(url, text=''):
    """Generate Facebook share URL"""
    return f"https://www.facebook.com/sharer/sharer.php?u={quote(url)}"


def get_twitter_share_url(url, text=''):
    """Generate Twitter share URL"""
    text_param = quote(text) if text else ''
    return f"https://twitter.com/intent/tweet?url={quote(url)}&text={text_param}"


def get_whatsapp_share_url(url, text=''):
    """Generate WhatsApp share URL"""
    full_text = f"{text} {url}" if text else url
    return f"https://wa.me/?text={quote(full_text)}"


def get_linkedin_share_url(url, text=''):
    """Generate LinkedIn share URL"""
    return f"https://www.linkedin.com/sharing/share-offsite/?url={quote(url)}"


def get_email_share_url(url, subject='', body=''):
    """Generate email share URL"""
    subject_param = quote(subject) if subject else ''
    body_param = quote(body) if body else quote(url)
    return f"mailto:?subject={subject_param}&body={body_param}"


def get_product_share_data(request, product):
    """Get all share data for a product"""
    url = get_product_share_url(request, product)
    text = f"Check out {product.name} on Mushanai!"
    description = product.short_description or product.description[:200] if product.description else ''
    
    return {
        'url': url,
        'text': text,
        'title': product.name,
        'description': description,
        'image': product.primary_image.url if product.primary_image else None,
        'facebook': get_facebook_share_url(url, text),
        'twitter': get_twitter_share_url(url, text),
        'whatsapp': get_whatsapp_share_url(url, text),
        'linkedin': get_linkedin_share_url(url, text),
        'email': get_email_share_url(url, f"Check out {product.name}", f"{text}\n\n{url}"),
    }


def get_project_share_data(request, project):
    """Get all share data for a project"""
    url = get_project_share_url(request, project)
    text = f"Support {project.title} on Mushanai!"
    description = project.short_description or project.description[:200] if project.description else ''
    
    return {
        'url': url,
        'text': text,
        'title': project.title,
        'description': description,
        'image': project.image.url if project.image else None,
        'funding_percentage': project.funding_percentage,
        'facebook': get_facebook_share_url(url, text),
        'twitter': get_twitter_share_url(url, text),
        'whatsapp': get_whatsapp_share_url(url, text),
        'linkedin': get_linkedin_share_url(url, text),
        'email': get_email_share_url(url, f"Support {project.title}", f"{text}\n\n{url}"),
    }


def get_vendor_share_data(request, vendor):
    """Get all share data for a vendor"""
    url = get_vendor_share_url(request, vendor)
    try:
        vendor_profile = vendor.vendor_profile
        company_name = vendor_profile.company_name
        description = vendor_profile.description[:200] if vendor_profile.description else ''
    except:
        company_name = vendor.username
        description = ''
    
    text = f"Check out {company_name} on Mushanai!"
    
    return {
        'url': url,
        'text': text,
        'title': company_name,
        'description': description,
        'image': vendor_profile.logo.url if hasattr(vendor, 'vendor_profile') and vendor.vendor_profile.logo else None,
        'facebook': get_facebook_share_url(url, text),
        'twitter': get_twitter_share_url(url, text),
        'whatsapp': get_whatsapp_share_url(url, text),
        'linkedin': get_linkedin_share_url(url, text),
        'email': get_email_share_url(url, f"Check out {company_name}", f"{text}\n\n{url}"),
    }

