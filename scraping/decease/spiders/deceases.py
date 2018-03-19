import random

import scrapy
from annoying.functions import get_object_or_None

from deceases.models import Symptom, DeceaseSymptom, Decease, Sphere


class SymptomSpider(scrapy.Spider):
    name = "Decease"

    def start_requests(self):
        urls = [
            'https://online-diagnos.ru/illness',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.get_urls)

    def get_urls(self, response):
        urls = response.css('#list_folclore_main').xpath('./li/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url=f'https://online-diagnos.ru{url}', callback=self.parse)

    def parse(self, response):
        deceases = response.css('.category_illness_list').xpath('.//li/a/@href').extract()
        for decease_link in deceases:
            yield scrapy.Request(response.urljoin(decease_link), callback=self.parse_decease)

    def parse_decease(self, response):
        sphere = response.xpath('//ul[@id="list_folclore_main"]/li[contains(@class,"active")]/a/text()').extract_first()
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
        sphere, _ = Sphere.objects.get_or_create(name=sphere)
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
            decease.sphere = sphere
            decease.save()
        else:
            decease = Decease.objects.create(name=name, description=description, passing=passing,
                                             diagnostics=diagnostics, treatment=treatment,
                                             recommendations=recommendations, chronic=chronic,
                                             contagiousness=contagiousness, malignancy=malignancy, duration=duration,
                                             sphere=sphere)

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
            'malignancy': malignancy,
            'sphere': sphere,

        }
