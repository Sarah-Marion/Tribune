from django.test import TestCase
from .models import Editor, Article, tag
import datetime as dt


# Create your tests here.
class EditorTestClass(TestCase):

    # Set up method
    def setUp(self):
        self.sarah = Editor(first_name = 'Sarah', last_name ='Marion', email ='devsarahmarion@gmail.com')

    def test_instantiation(self):
        self.assertEquals(self.sarah.first_name, 'Sarah')

    # Testing Instance
    def test_instance(self):
        self.assertTrue(isinstance(self.sarah, Editor))


    # Testing Save Method
    def test_save_method(self):
        self.sarah.save_editor()
        editors = Editor.objects.all()
        self.assertTrue(len(editors) > 0)



# Testing the Article model
class ArticleTestClass(TestCase):

    def setUp(self):
        # Creating a new editor and saving it

        self.sarah = Editor(first_name = 'Sarah', last_name ='Marion', email ='devsarahmarion@gmail.com')
        self.sarah.save_editor()

        #Creating a new tag and saving it
        
        self.new_tag = tag(name = 'testing')
        self.new_tag.save()

        self.new_article= Article(title = 'Test Article', post='This is a random test Post', editor = self.sarah)
        self.new_article.save()

        self.new_article.tag.add(self.new_tag)


    def tearDown(self):
        Editor.objects.all().delete()
        tag.objects.all().delete()
        Article.objects.all().delete()


    def test_get_news_today(self):
        today_news = Article.today_news()
        self.assertTrue(len(today_news)>0)


    def test_get_news_by_date(self):
        test_date = '2017-03-17'
        date = dt.datetime.strptime(test_date, '%Y-%m-%d').date()
        news_by_date = Article.days_news(date)
        self.assertTrue(len(news_by_date) == 0)