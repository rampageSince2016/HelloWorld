#    def createTab(self):
#        FACT_SERVICE_DIR_SQL = '''create table if not exists FACT_SERVICE_DIR(
#             id int(11) not null auto_increment, 
#             name varchar(100),
#             primary key (id)
#             ) engine=InnoDB
#            '''
#        FACT_SERVICE_SQL = '''create table if not exists FACT_SERVICE_SQL(
#             id int(11) not null auto_increment, 
#             name varchar(100),
#             serivce_dir_id int(11),
#             primary key (id),
#             forign key (serivce_dir_id) references FACT_SERVICE_DIR(id) ON UPDATE CASCADE ON DELETE RESTRICT,
#             index (service_dir_id)
#             ) engine=InnoDB
#            '''
#        FACT_SCENE_SQL = '''create table if not exists FACT_SCENE(
#             id int(11) not null auto_increment, 
#             name varchar(100),
#             serivce_id int(11),
#             primary key (id),
#             forign key (serivce_id) references FACT_SERVICE(id) ON UPDATE CASCADE ON DELETE RESTRICT,
#             index (service_id)
#             ) engine=InnoDB
#            '''
#        FACT_ATTR_SET_SQL = '''create table if not exists FACT_ATTR_SET(
#             id int(11) not null auto_increment, 
#             name varchar(100),
#             scene_id int(11),
#             primary key (id),
#             forign key (scene_id) references FACT_SCENE(id) ON UPDATE CASCADE ON DELETE RESTRICT,
#             index (scene_id)
#             ) engine=InnoDB
#            '''
#        FACT_ATTR = '''create table if not exists FACT_ATTR(
#             id int(11) not null auto_increment, 
#             name varchar(100),
#             type_id int(11),
#             value varchar(255),
#             attr_set_id int(11),
#             primary key (id),
#             forign key (attr_set_id) references FACT_ATTR_SET(id) ON UPDATE CASCADE ON DELETE RESTRICT,
#             index (attr_set_id)
#             ) engine=InnoDB
#            '''
#        DIM_TYPE = '''create table if not exists DIM_TYPE(
#             id int(11) not null auto_increment, 
#             name varchar(100),
#             name_zh varchar(150),
#             ) engine=InnoDB
#            '''
