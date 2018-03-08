import random

import scrapy
from annoying.functions import get_object_or_None

from deceases.models import Symptom, DeceaseSymptom, Decease


class SymptomSpider(scrapy.Spider):
    name = "Decease"

    def start_requests(self):
        urls = [
            'https://online-diagnos.ru/illness/c/bolezni-kostey-i-sustavov',
            'https://online-diagnos.ru/illness/c/bolezni-organov-dihaniya',
            'https://online-diagnos.ru/illness/c/endokrinnie-bolezni-i-narushenie-obmena-veschestv',
            'https://online-diagnos.ru/illness/c/bolezni-glaz'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        deceases = response.css('.category_illness_list').xpath('.//li/a/@href').extract()
        for decease_link in deceases:
            yield scrapy.Request(response.urljoin(decease_link), callback=self.parse_decease)

    # class Decease(models.Model):
    #     symptoms = models.ManyToManyField(to=Symptom, through='DeceaseSymptom')
    #     treatment = models.TextField()
    # recommendations = models.TextField(blank=True, null=True)

    def parse_decease(self, response):
        name = response.css('.title-h1::text').extract_first().strip()
        description = response.xpath(
            '//h2[contains(text(),"Общее описание") or contains(text(), "общее описание")]/following-sibling::p/text()').extract_first()
        if not name or not description:
            return
        passing = response.xpath(
            '//h2[contains(text(),"Клиническая картина") or contains(text(), "клиническая картина")]/following-sibling::p/text()').extract_first()
        diagnostics = response.xpath(
            '//h2[contains(text(),"Диагностика") or contains(text(), "диагностика")]/following-sibling::p/text()').extract_first()
        treatment = response.xpath(
            '//h2[contains(text(),"Лечение") or contains(text(), "лечение")]/following-sibling::p/text()').extract_first()
        recommendations = response.xpath(
            '//h2[contains(text(),"Рекомендации") or contains(text(), "рекомендации")]/following-sibling::p/text()').extract_first()
        chronic = 'хроничес' in description
        contagiousness = 100 if 'инфекц' in description else 0

        malignancy = random.choice([x for x in range(0, 100, 10)])
        duration = random.choice([5, 10, 20, 30, 100, 365])
        assert 'опасн' not in description or malignancy != 10
        symptoms_names = response.xpath(
            '//h2[contains(text(),"Симптомы") or contains(text(), "симптомы")]/following-sibling::*[not(position() > 1)]/li/text()').extract()
        symptoms = []
        decease = get_object_or_None(Decease, name=name)
        if decease:
            decease.description = description
            decease.passing = passing
            decease.diagnostic = diagnostics
            decease.treatment = treatment
            decease.recommendations = recommendations
            decease.chronic = chronic
            decease.contagiousness = contagiousness
            decease.malignancy = malignancy
            decease.duration = duration
            decease.save()
        else:
            decease = Decease.objects.create(name=name, description=description, passing=passing,
                                             diagnostics=diagnostics, treatment=treatment,
                                             recommendations=recommendations, chronic=chronic,
                                             contagiousness=contagiousness, malignancy=malignancy, duration=duration)

        for s in symptoms_names:
            symptom, _ = Symptom.objects.get_or_create(name=s)
            symptoms.append(symptom)
        for s in symptoms:
            DeceaseSymptom.objects.get_or_create(decease=decease, symptom=s)
        symptoms_table = response.css('.symptoms-frequency').xpath('.//tr')
        tr_names = symptoms_table.xpath('.//td[1]//text()').extract()
        tr_frequency = symptoms_table.xpath('.//td[2]/text()').extract()
        for name, frequency in zip(tr_names, tr_frequency):
            symptom, _ = Symptom.objects.get_or_create(name=name)
            if decease.occurrence < 100:
                decease.occurrence = 100
                decease.save()

            symptom_decease, _ = DeceaseSymptom.objects.get_or_create(symptom=symptom, decease=decease)
            symptom_decease.chances = frequency[:-1]
            symptom_decease.occurrence = int(frequency[:-1])
            symptom_decease.save()

        if not all([name, description, treatment]):
            if not name:
                raise AssertionError('name')
            if not description:
                raise AssertionError('description')
        yield {
            # 'name': name,
            # 'description': description,
            # 'chronic': chronic,
            # 'contagiousness': contagiousness,
            # 'passing': passing,
            # 'diagnostics': diagnostics,
            # 'treatment': treatment,
            'malignancy': malignancy

        }
        # name = response.xpath('//h1/span/text()').extract_first()
        # description = response.css('.description').xpath('.//p/text()').extract_first()
        # age = response.css('.thumbHolder .agerate::text').extract_first()
        # video_url = response.css('#videoHolder').xpath('iframe/@src').extract()
        # response = response.css('.film-detail')
        # genres = response.xpath('.//p[contains(text(),"Жанр")]/a/text()').extract()
        # cast = response.xpath('.//p[contains(text(),"Актёры")]//text()').extract()
        # directors = response.xpath('.//p[contains(text(),"Режиссёр")]//text()').extract()
        # duration = response.xpath('.//p[contains(text(),"Продолжительность")]/span[1]/text()').extract_first()
        # image_url = response.css('.thumbHolder').xpath('.//a//img/@src').extract_first()
        # required = [name, description, genres, cast, directors]
        # genres = list(filter(lambda x: x.strip() not in [',', '...', '.', ''], genres))[1:]
        # cast = list(filter(lambda x: x.strip() not in [',', '...', '.', ''], cast))[1:]
        # directors = list(filter(lambda x: x.strip() not in [',', '...', '.', ''], directors))[1:]
        # if description:
        #     description.replace('\n', '')
        # if age:
        #     age = age[:-1]
        # if duration:
        #     duration = re.findall(r'[0-9]{1,2}', duration)
        #     if not duration:
        #         duration.append(0)
        #     if len(duration) == 1:
        #         duration.append(0)
        #     duration = int(duration[0]) * 60 + int(duration[1])
        # if all(required):
        #     _genres = []
        #     _cast = []
        #     _directors = []
        #     for genre in genres:
        #         g = get_object_or_None(Genre, name=genre)
        #         if not g:
        #             g = Genre(name=genre)
        #             g.save()
        #         _genres.append(g)
        #     for actor in cast:
        #         g = get_object_or_None(Actor, name_surname=actor)
        #         if not g:
        #             g = Actor(name_surname=actor)
        #             g.save()
        #         _cast.append(g)
        #     for director in directors:
        #         g = get_object_or_None(Director, name_surname=director)
        #         if not g:
        #             g = Director(name_surname=director)
        #             g.save()
        #         _directors.append(g)
        #     if not age:
        #         age = 3
        #
        #     img_temp = NamedTemporaryFile(delete=True)
        #     img_temp.write(urllib.request.urlopen('https://kinoafisha.ua' + image_url).read())
        #     img_temp.flush()
        #
        #     film = Film(name=name, description=description,
        #                 date_release=date.today(), age=age, duration_minutes=duration, video_url=video_url)
        #     film.vertical_image.save(image_url.split('/')[-1], File(img_temp))
        #     film.horizontal_image.save(image_url.split('/')[-1], File(img_temp))
        #     film.big_image.save(image_url.split('/')[-1], File(img_temp))
        #     print(_cast)
        #     print(_directors)
        #     print(_genres)
        #     for actor in _cast:
        #         film.cast.add(actor)
        #     for director in _directors:
        #         film.directors.add(director)
        #     for genre in _genres:
        #         film.genres.add(genre)
        #     film.save()
        #
        # yield {
        #     # 'film_name': name,
        #     # 'genres': genres,
        #     'description': description,
        #     # 'age': age,
        #     # 'cast': cast,
        #     # 'producers': producers,
        #     # 'video_url': video_url,
        #     # 'duration': duration,
        #     # 'image_url': image_url,
        # }
