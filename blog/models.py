from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from datetime import date
from modelcluster.models import ParentalKey, ParentalManyToManyField
from wagtail.snippets.models import register_snippet
from django import forms
from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager

class blogIndexpage(Page):
    description = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("description")]

    def get_context(self, request):
        context = super().get_context(request)
        blogposts = self.get_children().live().order_by("-first_published_at")
        context["blogposts"] = blogposts
        return context

class blogPostTag(TaggedItemBase):
      content_object = ParentalKey("blogPostPage", related_name="tagged_items",
                                    on_delete=models.CASCADE)

class blogPostPage(Page):
     date = models.DateField("post Date", default=date.today)
     intro = RichTextField(blank=True)
     body = RichTextField(blank=True)
     author = ParentalManyToManyField("blog.Author", blank=True)
     tags = ClusterTaggableManager(through=blogPostTag, blank=True)

     def main_image(self):
         thumbnail = self.image_gallery.first()
         if thumbnail:
                return thumbnail.image
         else:
                return None

     content_panels = Page.content_panels + [FieldPanel("date"),
                                             FieldPanel("author", widget= forms.CheckboxSelectMultiple),
                                             FieldPanel("intro"),
                                             FieldPanel("body"), 
                                             InlinePanel("image_gallery",label="gallery_images"),
                                             FieldPanel("tags")]


class blogPageImageGallery(Orderable):
    page = ParentalKey(blogPostPage, related_name="image_gallery", 
                       on_delete=models.CASCADE)
    image = models.ForeignKey("wagtailimages.Image", related_name="+", 
                              on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, blank=True)
    panels = [FieldPanel("image"), FieldPanel("caption")]


@register_snippet      
class Author(models.Model):
      name = models.CharField(max_length=225)       
      author_image = models.ForeignKey("wagtailimages.image", related_name="+",
                                        on_delete=models.CASCADE)

      panels = [FieldPanel("name"), FieldPanel("author_image")]

      def __str__(self):
            return self.name
      
      
class TagIndexPage(Page):
      def get_context(self, request):
          tag = request.GET.get("tag")
          blogposts = blogPostPage.objects.filter(tags__name=tag)

          context = super().get_context(request)
          context["blogposts"] = blogposts
          return context