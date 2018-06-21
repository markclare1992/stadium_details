library(mongolite)
library(tidyverse)
library(RColorBrewer)
match_weather<-mongo(collection='match_weather',db='opta')
stad_alt<-mongo(collection = 'stadiums',db='opta')
altitude<-stad_alt$find()
altitude$elevation=altitude$altitude_data$elevation
altitude<-altitude %>% select(venueName,elevation)
df<-match_weather$find()
default_colors = c("#468CDE","#52D273","#E94F64","#E5C454","#D6DBDE","#E57254","#656565")

ggplot(aes(x=elevation),data=altitude)+
  stat_bin(fill="#E5C454",alpha=.75,bins=15)+
  theme_github()+
  geom_hline(yintercept = 0, size=.75)+
  labs(x='Elevation (m)', y='Count', 
       title="Altitude",
       subtitle="Stadiums from various top leagues",
       caption="Data from googlemapsapi")+
  theme(plot.title=element_text(face="bold"))+
  theme(plot.subtitle=element_text(margin=margin(b=10)))+
  theme(plot.caption=element_text(size=8, margin=margin(t=10)))+
  guides(shape = guide_legend(override.aes = list(shape = 15)))


ggplot(data=df)+
  stat_density(aes(x=temperature,color=tournament),position = 'identity',geom='line')+
  scale_color_manual(values=default_colors)+
  scale_x_continuous(expand=c(0,0),breaks=seq(-25, 45, by=5),limits = c(-25,40))+
  theme_github()+
  geom_hline(yintercept = 0, size=.75)+
  theme(legend.position = 'bottom', legend.title = element_blank(), 
        legend.key = element_blank())+
  labs(x='Temperature °C', y='Density', 
       title="Density plot for temperature at kick off",
       subtitle="Top 5 European leagues: 2017-2018",
       caption="Data from darksky.net")+
  theme(plot.title=element_text(face="bold"))+
  theme(plot.subtitle=element_text(margin=margin(b=10)))+
  theme(plot.caption=element_text(size=8, margin=margin(t=10)))+
  guides(shape = guide_legend(override.aes = list(shape = 15)))


df %>% group_by(summary) %>% summarise(n=n()) %>% arrange(-n) %>% 
  ggplot()+
  geom_col(aes(y=n,x=reorder(summary,-n,sum)),fill="#E5C454")+
  theme_github()+
  theme(axis.text.x = element_text(angle = 90, vjust=0.5, hjust=1))+
  labs(x='Condition', y='Count', 
       title="Weather conditions at kick off",
       subtitle="Top 5 European leagues: 2017-2018",
       caption="Data from darksky.net")+
  theme(plot.title=element_text(face="bold"))+
  theme(plot.subtitle=element_text(margin=margin(b=10)))+
  theme(plot.caption=element_text(size=8, margin=margin(t=10)))
  


stadium_dims<-mongo(collection='stadium_dims',db='opta')
stad_df<-stadium_dims$find() %>% 
  filter(tournamentId==2) %>% 
  filter(dimensions!='unknown')

ggplot(aes(x=dimensions_length,y=dimensions_width,label=venueName),
       data=stad_df)+
  geom_jitter(size=3,alpha=.75,color="#E5C454")+
  scale_color_manual(values=default_colors)+
  theme_github()+
  coord_cartesian(xlim=c(90,140),ylim=c(50,100))+
  labs(x='Length (m)', y='Width (m)', 
       title="Pitch Dimensions",
       subtitle="Premier League stadiums",
       caption="Data from wikipedia")+
  theme(plot.title=element_text(face="bold"))+
  theme(plot.subtitle=element_text(margin=margin(b=10)))+
  theme(plot.caption=element_text(size=8, margin=margin(t=10)))
  
