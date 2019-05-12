# Twig your health 
### Idea
Nowadays people have really mad pace of life and not always have enough time to look after themselves. 
Sometimes they get different deseases, illnesses and even simple cold  and not everyone has an opportunity 
to visit a specialist, when he really needs this. Sometimes it happens because the doctors has 
a schedule as a patient has and he simply cant leave his work. Also because of a long queues
to medical experts and sometimes rude people there who they have to deal with. As we live in a big city, 
the problem with traffic jams is also very common, so to visit doctor in lunch break also can be impossible.
This matter of fact is precisely a main reason for creating this web-page, 
which can help not only for saving patients time, but also for saving his nerves. 
Also the patient  can get day-and-night consultation by HIS real doctor, who he can choose, 
which isn’t possible with simple district doctor. Also an access to secret chat with an opportunity
to send a photo can be very useful for them, who cant leave home if the illness is in the face, 
for example, and person hesitates to go outside with it or just cant move because of high temperature
or broken leg, for example. In fact, “TwigYourHealth” can be very useful for people, because there isn’t good 
and simple analogues in the internet as this web-site, which the patient can use at any time.
And the most reason relevance of our product – is that people always get illnesses and they always
need someones help to stay healthy. 
### Goal
Our business aim is to provide comfortable service for people 
who don’t want to spend their time for visiting hospitals and searching good specialists.
### Customers
Patients and doctors of any age.
## Developers
* [Aleksieieva Valeriia](https://github.com/Lerika011) - Business analytic
* [Nikita Chernenko](https://github.com/marakaci) - Full Stack developer
* [Nikolay Lukianov](https://github.com/nicklukk) - Backend End developer
* [Oliinyk Taisiia](https://github.com/Taya27) - Front End developer
* [Pivtorak Kateryna](https://github.com/KatyaKrasavchik) - Designer, tester


##To run the project
Install docker and docker-compose.
Go to folder "docker".
run `docker-compose up`.
Go to `0.0.0.0:8000` in browser

##To save data
Run 
docker exec twig_your_health_django /bin/bash -c "python manage.py save_staging accounts communication deceases notifications payments timetables --settings=base_settings"
