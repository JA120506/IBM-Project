import math

# Translation matrices for dashboard texts and reports
TRANSLATIONS = {
    "es": {
        "title": "Evaluación de Inundación",
        "score_label": "Puntuación de Amenaza",
        "telemetry_title": "Diagnósticos de Telemetría",
        "col_measure": "Medición",
        "col_val": "Valor Actual",
        "col_status": "Estado del Límite",
        "metric_7d": "Lluvia Acumulada 7 Días",
        "metric_peak24h": "Lluvia Máxima 24h",
        "metric_intensity": "Intensidad Horaria Máx",
        "metric_discharge": "Descarga Máxima del Río",
        "metric_consec": "Días Lluviosos Consecutivos",
        "status_excessive": "Excesivo",
        "status_elevated": "Elevado",
        "status_normal": "Normal",
        "status_heavy": "Fuerte",
        "status_moderate": "Moderado",
        "status_light": "Ligero",
        "status_torrid": "Torrencial",
        "status_saturated": "Suelo Saturado",
        "status_damp": "Suelo Húmedo",
        "status_receptive": "Suelo Receptivo",
        "status_surge": "Oleada de línea base",
        "status_no_sensor": "Sin Sensor de Río",
        "threat_analysis_title": "Análisis Detallado de Amenazas",
        "threat_flash": "Potencial de Inundación Relámpago",
        "threat_river": "Desbordamiento de Río / Canal",
        "threat_soil": "Saturación del Suelo y Velocidad de Escorrentía",
        "safety_protocols_title": "Protocolos de Seguridad Requeridos",
        "peak_time_msg": "Se anticipa el evento de precipitación más pesado el",
        "situations": {
            "EXTREME": "**EMERGENCIA CRÍTICA POR INUNDACIÓN:** Se avecina una combinación severa de lluvias extremas ({total_precip}mm pronosticadas) y un aumento del caudal del río. La descarga del río proyecta subir a **{peak_discharge} m³/s** ({multiplier}x nivel normal). Se requiere acción inmediata para proteger vidas y propiedades.",
            "HIGH": "**ALERTA DE ALTO RIESGO:** Los indicadores meteorológicos muestran un riesgo sustancial de inundación. Precipitación total estimada de **{total_precip} mm** con un aguacero diario máximo de **{max_daily} mm**. Los canales de escorrentía experimentarán una carga pesada.",
            "MODERATE": "**AVISO MODERADO:** Los patrones climáticos activos traerán lluvias acumuladas de **{total_precip} mm** durante la semana. Si bien no se esperan inundaciones generales, pueden ocurrir problemas locales de drenaje.",
            "LOW": "**CONDICIONES NORMALES:** El pronóstico meteorológico indica condiciones secas o lluvias muy ligeras ({total_precip}mm acumulados). Las métricas hidrológicas permanecen estables y dentro de los límites de seguridad."
        },
        "flash_statuses": {
            "EXTREME": "⚠️ **CRÍTICO:** La precipitación horaria de alta intensidad (pico de **{max_hourly} mm/h**) abrumará el drenaje pluvial urbano a los pocos minutos del inicio, creando inundaciones repentinas generalizadas.",
            "HIGH": "⚠️ **ALTO:** Fuertes ráfagas de lluvia (hasta **{max_hourly} mm/h**) representan una gran amenaza de inundaciones de calles e inundaciones localizadas en áreas urbanas.",
            "MODERATE": "⚠️ **MODERADO:** La precipitación horaria de **{max_hourly} mm/h** puede causar inundaciones menores en calles y acumulación de agua en intersecciones mal drenadas.",
            "LOW": "⚠️ **INSIGNIFICANTE:** No se proyectan eventos de lluvia de alta intensidad. Las inundaciones repentinas son muy improbables."
        },
        "river_statuses": {
            "EXTREME": "🌊 **CRÍTICO:** Se excederá la capacidad del río a medida que la descarga aumente de {start_discharge} m³/s a **{peak_discharge} m³/s**. Desbordamientos en zonas bajas son casi seguros.",
            "HIGH": "🌊 **MODERADO A ALTO:** La descarga del río alcanza un pico de **{peak_discharge} m³/s** ({multiplier}x incremento). Es probable que ocurran desbordamientos menores en las riberas.",
            "MODERATE": "🌊 **BAJO A MODERADO:** Los niveles del río aumentarán pero se mantendrán mayormente dentro de los límites de contención (descarga pico: **{peak_discharge} m³/s**).",
            "LOW": "🌊 **ESTABLE:** El flujo del río es normal, manteniéndose seguro alrededor de **{peak_discharge} m³/s**."
        },
        "river_statuses_fallback": {
            "EXTREME": "🌊 **ALTO:** Se espera que las fuertes escorrentías locales causen desbordamientos graves en arroyos y drenajes debido a la intensa descarga superficial.",
            "HIGH": "🌊 **MODERADO:** Se esperan inundaciones localizadas y aumentos rápidos en canales pequeños y arroyos.",
            "MODERATE": "🌊 **BAJO:** Los arroyos y canales locales verán niveles crecientes pero se mantendrán dentro de sus cauces.",
            "LOW": "🌊 **ESTABLE:** Los niveles de arroyos y canales se encuentran en sus niveles estacionales de referencia."
        },
        "soil_statuses": {
            "EXTREME": "🌱 **SATURADO:** El suelo saturado por {consecutive_days} días consecutivos de lluvia evitará la absorción, dirigiendo el 90%+ de la lluvia directamente a la escorrentía superficial.",
            "HIGH": "🌱 **MUY HÚMEDO:** Alto contenido de humedad en el suelo. La capacidad de absorción disminuye significativamente, lo que provoca un rápido inicio de la escorrentía.",
            "MODERATE": "🌱 **MODERADAMENTE HÚMEDO:** El suelo tiene una capacidad moderada para absorber la lluvia, pero la humedad persistente disminuirá la absorción al final de la semana.",
            "LOW": "🌱 **SECO / RECEPTIVO:** El suelo muestra un alto potencial de absorción. La lluvia se filtrará directamente en los acuíferos."
        },
        "actions": {
            "EXTREME": [
                "**EVACUAR ZONAS BAJAS:** Si lo indican las autoridades locales, evacúe de inmediato. No espere a que el agua bloquee las rutas de escape.",
                "**NUNCA CRUCE CORRIENTES DE AGUA:** Solo 15 cm de agua en movimiento pueden derribarlo, y 60 cm pueden arrastrar vehículos.",
                "**PREPARE KIT DE EMERGENCIA:** Mantenga documentos, alimentos secos, agua limpia y cargadores listos. Mueva objetos de valor al nivel más alto."
            ],
            "HIGH": [
                "**MONITOREE ACTUALIZACIONES:** Siga las transmisiones de los servicios meteorológicos locales para alertas de inundaciones repentinas.",
                "**ASEGURE EL EXTERIOR:** Mueva objetos sueltos al interior y verifique que las canaletas y desagües estén limpios.",
                "**PLANIFIQUE RUTAS:** Evite pasos a desnivel y caminos adyacentes a ríos durante los picos de lluvia."
            ],
            "MODERATE": [
                "**LIMPIE CANALETAS:** Asegúrese de que las canaletas domésticas y desagües estén libres de hojas y escombros.",
                "**CONDUZCA CON PRECAUCIÓN:** Conduzca con cuidado durante las lluvias y evite pasar por zonas con acumulación de agua profunda.",
                "**VERIFIQUE SUMINISTROS:** Asegúrese de tener a mano suministros básicos (linternas, botiquín)."
            ],
            "LOW": [
                "**SIN ACCIONES INMEDIATAS:** No se requieren medidas de protección contra inundaciones en este momento.",
                "**MANTENIMIENTO DE RUTINA:** Realice controles regulares en canaletas domésticas y sistemas de drenaje."
            ]
        }
    },
    "hi": {
        "title": "बाढ़ जोखिम मूल्यांकन",
        "score_label": "जोखिम स्कोर",
        "telemetry_title": "टेलीमेट्री डायग्नोस्टिक्स",
        "col_measure": "माप",
        "col_val": "वर्तमान मान",
        "col_status": "सीमा स्थिति",
        "metric_7d": "7-दिवसीय संचयी वर्षा",
        "metric_peak24h": "अधिकतम 24 घंटे की वर्षा",
        "metric_intensity": "अधिकतम प्रति घंटा वर्षा दर",
        "metric_discharge": "अधिकतम नदी जल प्रवाह",
        "metric_consec": "लगातार बारिश वाले दिन",
        "status_excessive": "अत्यधिक",
        "status_elevated": "बढ़ा हुआ",
        "status_normal": "सामान्य",
        "status_heavy": "भारी",
        "status_moderate": "मध्यम",
        "status_light": "हल्की",
        "status_torrid": "अत्यंत तीव्र",
        "status_saturated": "संतृप्त मिट्टी",
        "status_damp": "गीली मिट्टी",
        "status_receptive": "सोखने योग्य मिट्टी",
        "status_surge": "आधार रेखा वृद्धि",
        "status_no_sensor": "कोई नदी सेंसर नहीं",
        "threat_analysis_title": "जोखिम विश्लेषण विवरण",
        "threat_flash": "अचानक बाढ़ (फ़्लैश फ़्लड) की संभावना",
        "threat_river": "नदी / नहर जल स्तर अतिप्रवाह",
        "threat_soil": "मिट्टी की संतृप्ति और बहाव वेग",
        "safety_protocols_title": "आवश्यक सुरक्षा प्रोटोकॉल",
        "peak_time_msg": "सबसे भारी बारिश होने की संभावना है:",
        "situations": {
            "EXTREME": "**गंभीर बाढ़ आपातकाल:** अत्यधिक बारिश ({total_precip}mm अनुमानित) और भारी जल प्रवाह का एक गंभीर संयोजन आसन्न है। नदी का बहाव बढ़कर **{peak_discharge} m³/s** ({multiplier}x सामान्य स्तर) होने का अनुमान है। जान-माल की सुरक्षा के लिए तत्काल कार्रवाई आवश्यक है।",
            "HIGH": "**उच्च जोखिम चेतावनी:** मौसम संबंधी संकेतकों से बाढ़ का महत्वपूर्ण खतरा दिखाई दे रहा है। कुल अनुमानित वर्षा **{total_precip} mm** है, जिसमें अधिकतम दैनिक बारिश **{max_daily} mm** है। जल निकासी मार्गों पर अत्यधिक दबाव रहेगा।",
            "MODERATE": "**मध्यम सलाह:** सक्रिय मौसम प्रणालियों के कारण सप्ताह के दौरान कुल **{total_precip} mm** बारिश होगी। हालांकि आम तौर पर बाढ़ की संभावना नहीं है, स्थानीय जलभराव की समस्या हो सकती है।",
            "LOW": "**सामान्य मौसम स्थिति:** मौसम का पूर्वानुमान शुष्क या बहुत हल्की बारिश ({total_precip}mm संचयी) का संकेत देता है। जल विज्ञान संबंधी आंकड़े स्थिर और सुरक्षित सीमाओं के भीतर हैं।"
        },
        "flash_statuses": {
            "EXTREME": "⚠️ **गंभीर:** अत्यधिक तीव्र वर्षा दर (अधिकतम **{max_hourly} mm/h**) शुरू होने के कुछ ही मिनटों के भीतर शहरी तूफानी जल निकासी को पंगु बना देगी, जिससे व्यापक अचानक बाढ़ आ जाएगी।",
            "HIGH": "⚠️ **उच्च:** भारी बारिश की बौछारें (अधिकतम **{max_hourly} mm/h**) शहरी क्षेत्रों में सड़कों पर जलभराव और अचानक बाढ़ का उच्च खतरा पैदा करती हैं।",
            "MODERATE": "⚠️ **मध्यम:** **{max_hourly} mm/h** की प्रति घंटा बारिश के कारण सड़कों पर मामूली जलभराव और जल निकासी विहीन चौराहों पर पानी जमा हो सकता है।",
            "LOW": "⚠️ **नगण्य:** अत्यधिक वर्षा की कोई संभावना नहीं है। अचानक बाढ़ आने की संभावना बहुत कम है।"
        },
        "river_statuses": {
            "EXTREME": "🌊 **गंभीर:** नदी जल प्रवाह क्षमता पार हो जाएगी क्योंकि बहाव {start_discharge} m³/s से बढ़कर **{peak_discharge} m³/s** हो जाएगा। निचले इलाकों में बाढ़ आना लगभग तय है।",
            "HIGH": "🌊 **मध्यम से उच्च:** नदी का प्रवाह **{peak_discharge} m³/s** ({multiplier}x वृद्धि) के शिखर पर पहुंच जाएगा। नदी के किनारों पर आंशिक अतिप्रवाह होने की संभावना है।",
            "MODERATE": "🌊 **कम से मध्यम:** नदी का जल स्तर बढ़ेगा लेकिन अधिकांशतः नियंत्रण सीमाओं के भीतर रहेगा (अधिकतम बहाव: **{peak_discharge} m³/s**)।",
            "LOW": "🌊 **स्थिर:** नदी का प्रवाह सामान्य है, जो **{peak_discharge} m³/s** के सुरक्षित स्तर पर बना हुआ है।"
        },
        "river_statuses_fallback": {
            "EXTREME": "🌊 **उच्च:** तीव्र सतही जल बहाव के कारण स्थानीय नालों और सहायक नदियों में गंभीर उफान आने की आशंका है।",
            "HIGH": "🌊 **मध्यम:** स्थानीय नालों और छोटी जलधाराओं में जल स्तर में तेजी से वृद्धि होने की संभावना है।",
            "MODERATE": "🌊 **कम:** छोटी नदियों और नालों का जल स्तर बढ़ेगा परंतु वे अपनी सीमाओं के भीतर ही बहेंगे।",
            "LOW": "🌊 **स्थिर:** नालों और छोटी जलधाराओं का स्तर मौसम के अनुकूल अपनी सामान्य सीमा में है।"
        },
        "soil_statuses": {
            "EXTREME": "🌱 **संतृप्त:** लगातार {consecutive_days} दिनों की बारिश से पूरी तरह संतृप्त हो चुकी मिट्टी अब पानी नहीं सोख पाएगी, जिससे 90%+ वर्षा का पानी सीधे तौर पर सतही बहाव में बदल जाएगा।",
            "HIGH": "🌱 **अत्यधिक गीली:** मिट्टी में नमी की मात्रा बहुत अधिक है। सोखने की क्षमता में काफी कमी आई है, जिससे पानी का बहाव तेजी से शुरू होगा।",
            "MODERATE": "🌱 **मध्यम गीली:** मिट्टी में बारिश सोखने की मध्यम क्षमता है, लेकिन लगातार नमी के कारण सप्ताह के अंत तक सोखने की दर में कमी आएगी।",
            "LOW": "🌱 **शुष्क / सोखने योग्य:** मिट्टी में पानी सोखने की उच्च क्षमता है। बारिश का पानी सीधे भूजल में समा जाएगा।"
        },
        "actions": {
            "EXTREME": [
                "**निचले इलाकों से तुरंत निकलें:** स्थानीय अधिकारियों के निर्देशानुसार तुरंत सुरक्षित स्थान पर जाएं। निकास मार्ग बंद होने का इंतजार न करें।",
                "**बहते पानी को पार न करें:** मात्र 15 सेमी बहता पानी आपको गिरा सकता है, और 60 सेमी पानी वाहनों को बहा ले जा सकता है।",
                "**आपातकालीन किट तैयार रखें:** महत्वपूर्ण दस्तावेज, सूखा भोजन, साफ पानी और पावर बैंक तैयार रखें। कीमती सामान घर की ऊपरी मंजिल पर रख दें।"
            ],
            "HIGH": [
                "**अपडेट पर नजर रखें:** अचानक बाढ़ की चेतावनियों के लिए स्थानीय मौसम समाचार चैनलों से जुड़े रहें।",
                "**बाहरी वस्तुओं को सुरक्षित करें:** बाहर रखी ढीली चीजों को अंदर लाएं और छतों तथा नालियों की सफाई सुनिश्चित करें।",
                "**मार्गों की योजना बनाएं:** अत्यधिक बारिश के दौरान नदी के पास की सड़कों और अंडरपास से यात्रा करने से बचें।"
            ],
            "MODERATE": [
                "**नालियों को साफ रखें:** सुनिश्चित करें कि घर की नालियां और पाइप पत्तों या कचरे से मुक्त हों।",
                "**सावधानी से वाहन चलाएं:** बारिश के दौरान सावधानीपूर्वक ड्राइव करें और गहरे जलभराव वाले रास्तों पर गाड़ी न ले जाएं।",
                "**आपातकालीन वस्तुओं की जांच करें:** टॉर्च, बैटरी और प्राथमिक चिकित्सा किट जैसी आवश्यक वस्तुएं संभाल कर रखें।"
            ],
            "LOW": [
                "**कोई तत्काल कार्रवाई नहीं:** वर्तमान में बाढ़ से सुरक्षात्मक उपायों की आवश्यकता नहीं है।",
                "**नियमित रखरखाव:** घर की जल निकासी प्रणालियों की नियमित जांच जारी रखें।"
            ]
        }
    },
    "fr": {
        "title": "Évaluation du Risque d'Inondation",
        "score_label": "Indice de Menace",
        "telemetry_title": "Diagnostics de Télémétrie",
        "col_measure": "Mesure",
        "col_val": "Valeur Actuelle",
        "col_status": "Statut de Seuil",
        "metric_7d": "Pluie Cumulée 7 Jours",
        "metric_peak24h": "Pluie Maximale 24h",
        "metric_intensity": "Intensité Horaire Max",
        "metric_discharge": "Débit Maximum du Cours d'Eau",
        "metric_consec": "Jours Pluvieux Consécutifs",
        "status_excessive": "Excessif",
        "status_elevated": "Élevé",
        "status_normal": "Normal",
        "status_heavy": "Forte",
        "status_moderate": "Modéré",
        "status_light": "Léger",
        "status_torrid": "Torrentiel",
        "status_saturated": "Sol Saturé",
        "status_damp": "Sol Humide",
        "status_receptive": "Sol Réceptif",
        "status_surge": "Hausse par rapport au niveau de référence",
        "status_no_sensor": "Pas de Capteur de Rivière",
        "threat_analysis_title": "Analyse Détaillée des Menaces",
        "threat_flash": "Risque de Crue Éclair",
        "threat_river": "Débordement de Rivière / Canal",
        "threat_soil": "Saturation du Sol & Vitesse de Ruissellement",
        "safety_protocols_title": "Protocoles de Sécurité Requis",
        "peak_time_msg": "L'événement de précipitations le plus intense est prévu le",
        "situations": {
            "EXTREME": "**URGENCE CRITIQUE INONDATION :** Une combinaison sévère de précipitations extrêmes ({total_precip}mm prévus) et d'une crue majeure est imminente. Le débit du cours d'eau devrait atteindre **{peak_discharge} m³/s** ({multiplier}x le niveau normal). Action immédiate requise pour protéger les vies et les biens.",
            "HIGH": "**ALERTE RISQUE ÉLEVÉ :** Les indicateurs météorologiques montrent un risque d'inondation substantiel. Précipitations totales prévues de **{total_precip} mm** avec une averse quotidienne maximale de **{max_daily} mm**. Les canaux d'évacuation subiront une forte pression.",
            "MODERATE": "**AVIS MODÉRÉ :** Des systèmes météorologiques actifs apporteront des pluies totalisant **{total_precip} mm** sur la semaine. Bien qu'aucune inondation générale ne soit attendue, des problèmes locaux de drainage peuvent survenir.",
            "LOW": "**CONDITIONS NORMALES :** Les prévisions météorologiques indiquent un temps sec ou des pluies très légères ({total_precip}mm cumulés). Les données hydrologiques restent stables et dans des limites de sécurité."
        },
        "flash_statuses": {
            "EXTREME": "⚠️ **CRITIQUE :** Des intensités de pluie horaires extrêmes (pic à **{max_hourly} mm/h**) satureront le drainage pluvial urbain en quelques minutes, provoquant des crues éclairs généralisées.",
            "HIGH": "⚠️ **ÉLEVÉ :** De fortes rafales de pluie (jusqu'à **{max_hourly} mm/h**) posent un risque élevé d'inondation des rues et de crues localisées en zone urbaine.",
            "MODERATE": "⚠️ **MODÉRÉ :** Des précipitations horaires de **{max_hourly} mm/h** peuvent provoquer des inondations de rue mineures et des accumulations d'eau aux intersections mal drainées.",
            "LOW": "⚠️ **NÉGLIGEABLE :** Aucun événement pluvieux de forte intensité n'est prévu. Les crues éclairs sont très peu probables."
        },
        "river_statuses": {
            "EXTREME": "🌊 **CRITIQUE :** La capacité du lit de la rivière sera dépassée, le débit augmentant de {start_discharge} m³/s à **{peak_discharge} m³/s**. Des inondations dans les plaines basses sont quasi certaines.",
            "HIGH": "🌊 **MODÉRÉ À ÉLEVÉ :** Le débit de la rivière culminera à **{peak_discharge} m³/s** (augmentation de {multiplier}x). Des débordements mineurs à modérés sont probables.",
            "MODERATE": "🌊 **BAS À MODÉRÉ :** Les cours d'eau vont monter mais resteront pour la plupart dans leurs limites de confinement (débit maximal : **{peak_discharge} m³/s**).",
            "LOW": "🌊 **STABLE :** Le débit de la rivière est normal, se maintenant en toute sécurité autour de **{peak_discharge} m³/s**."
        },
        "river_statuses_fallback": {
            "EXTREME": "🌊 **ÉLEVÉ :** Le ruissellement local intense devrait provoquer de graves débordements de ruisseaux et de collecteurs d'eaux pluviales.",
            "HIGH": "🌊 **MODÉRÉ :** Des inondations localisées et des hausses rapides de petits cours d'eau sont attendues.",
            "MODERATE": "🌊 **BAS :** Les ruisseaux et canaux locaux connaîtront des hausses de niveau mais resteront dans leurs lits.",
            "LOW": "🌊 **STABLE :** Les ruisseaux et canaux sont à leurs niveaux de référence saisonniers."
        },
        "soil_statuses": {
            "EXTREME": "🌱 **SATURÉ :** Le sol saturé après {consecutive_days} jours consécutifs de pluie empêchera toute absorption, envoyant plus de 90% des pluies directement vers le ruissellement de surface.",
            "HIGH": "🌱 **TRÈS HUMIDE :** Taux d'humidité du sol élevé. La capacité d'absorption est fortement réduite, entraînant un ruissellement rapide.",
            "MODERATE": "🌱 **MODÉRÉMENT HUMIDE :** Le sol a une capacité modérée d'absorption des pluies, mais l'humidité persistante diminuera l'absorption d'ici la fin de la semaine.",
            "LOW": "🌱 **SEC / RÉCEPTIF :** Le sol présente un fort potentiel d'absorption. La pluie s'infiltrera directement dans les nappes phréatiques."
        },
        "actions": {
            "EXTREME": [
                "**ÉVACUER LES ZONES BASSES :** Sur ordre des autorités, évacuez immédiatement. N'attendez pas que les routes soient bloquées par les eaux.",
                "**NE JAMAIS TRAVERSER LES EAUX DE CRUE :** 15 cm d'eau en mouvement peuvent vous renverser, et 60 cm peuvent emporter un véhicule.",
                "**PRÉPARER UN KIT D'URGENCE :** Gardez papiers, nourriture sèche, eau potable et batteries externes prêts. Déplacez les objets précieux à l'étage."
            ],
            "HIGH": [
                "**SUIVRE LES ALERTES :** Restez à l'écoute des bulletins météorologiques locaux pour suivre les alertes de crues éclairs.",
                "**SÉCURISER L'EXTÉRIEUR :** Rentrez les objets légers et vérifiez que les gouttières et drains sont dégagés.",
                "**PLANIFIER VOS DÉPLACEMENTS :** Évitez les passages souterrains et les routes longeant les cours d'eau en période de crue."
            ],
            "MODERATE": [
                "**NETTOYER LES GOUTTIÈRES :** Assurez-vous que les gouttières et descentes pluviales sont libres de débris.",
                "**CONDUIRE PRUDEMMENT :** Conduisez avec prudence par temps de pluie et ne traversez pas de flaques d'eau profondes.",
                "**VÉRIFIER VOS STOCKS :** Assurez-vous d'avoir des fournitures de secours de base (lampes torche, trousse de secours)."
            ],
            "LOW": [
                "**AUCUNE ACTION IMMÉDIATE :** Aucune mesure de protection contre les inondations n'est requise pour le moment.",
                "**ENTRETIEN DE ROUTINE :** Effectuez des vérifications de routine sur vos gouttières et systèmes de drainage."
            ]
        }
    },
    "bn": {
        "title": "বন্যা ঝুঁকি মূল্যায়ন",
        "score_label": "ঝুঁকি স্কোর",
        "telemetry_title": "টেলিমিত্রি ডায়াগনস্টিকস",
        "col_measure": "পরিমাপ",
        "col_val": "বর্তমান মান",
        "col_status": "সীমা অবস্থা",
        "metric_7d": "৭-দিনের সঞ্চিত বৃষ্টিপাত",
        "metric_peak24h": "সর্বোচ্চ ২৪ ঘণ্টার বৃষ্টিপাত",
        "metric_intensity": "সর্বোচ্চ প্রতি ঘণ্টার বৃষ্টিপাত",
        "metric_discharge": "সর্বোচ্চ নদীর পানি প্রবাহ",
        "metric_consec": "টানা বৃষ্টিপাতের দিন",
        "status_excessive": "অতিরিক্ত",
        "status_elevated": "উচ্চতর",
        "status_normal": "স্বাভাবিক",
        "status_heavy": "ভারী",
        "status_moderate": "মাঝারি",
        "status_light": "হালকা",
        "status_torrid": "চরম অতিবৃষ্টি",
        "status_saturated": "সম্পৃক্ত মাটি",
        "status_damp": "ভেজা মাটি",
        "status_receptive": "শোষণক্ষম মাটি",
        "status_surge": "বেসলাইন বৃদ্ধির হার",
        "status_no_sensor": "কোনো নদী সেন্সর নেই",
        "threat_analysis_title": "ঝুঁকি বিশ্লেষণ বিবরণ",
        "threat_flash": "হঠাৎ বন্যা (ফ্ল্যাশ ফ্লাড) হওয়ার সম্ভাবনা",
        "threat_river": "নদী / খালের পানি উপচে পড়া",
        "threat_soil": "মাটির সম্পৃক্ততা ও নিষ্কাশন গতি",
        "safety_protocols_title": "প্রয়োজনীয় নিরাপত্তা নির্দেশিকা",
        "peak_time_msg": "সবচেয়ে ভারী বৃষ্টিপাতের সম্ভাবনা রয়েছে:",
        "situations": {
            "EXTREME": "**চরম বন্যা সতর্কতা:** চরম বৃষ্টিপাত ({total_precip}mm পূর্বাভাস) এবং নদীর পানির উচ্চ প্রবাহের একটি মারাত্মক পরিস্থিতি আসন্ন। নদীর জলপ্রবাহ বৃদ্ধি পেয়ে **{peak_discharge} m³/s** ({multiplier}x স্বাভাবিক মাত্রা) হওয়ার সম্ভাবনা রয়েছে। জানমালের নিরাপত্তায় অবিলম্বে ব্যবস্থা গ্রহণ জরুরি।",
            "HIGH": "**উচ্চ ঝুঁকি সতর্কতা:** আবহাওয়ার ধরণ অনুযায়ী বন্যার একটি উল্লেখযোগ্য ঝুঁকি দেখা যাচ্ছে। মোট বৃষ্টিপাত **{total_precip} mm** এবং একদিনে সর্বোচ্চ বৃষ্টি **{max_daily} mm** হতে পারে। পানি নিষ্কাশন ব্যবস্থার ওপর ভারী চাপ পড়বে।",
            "MODERATE": "**মাঝারি পরামর্শ:** সক্রিয় আবহাওয়া পরিস্থিতির কারণে সপ্তাহে মোট **{total_precip} mm** বৃষ্টিপাত হতে পারে। সাধারণ বন্যার আশঙ্কা না থাকলেও স্থানীয় জলাবদ্ধতা তৈরি হতে পারে।",
            "LOW": "**স্বাভাবিক অবস্থা:** শুষ্ক আবহাওয়া বা অতি হালকা বৃষ্টিপাতের ({total_precip}mm সঞ্চিত) সম্ভাবনা রয়েছে। হাইড্রোলজিক্যাল সূচকসমূহ স্বাভাবিক এবং নিরাপদ সীমার মধ্যে রয়েছে।"
        },
        "flash_statuses": {
            "EXTREME": "⚠️ **গুরুতর:** অত্যন্ত তীব্র বৃষ্টিপাতের হার (সর্বোচ্চ **{max_hourly} mm/h**) শুরু হওয়ার মাত্র কয়েক মিনিটের মধ্যে শহরের নিষ্কাশন ব্যবস্থাকে অচল করে ব্যাপক হঠাৎ বন্যা সৃষ্টি করবে।",
            "HIGH": "⚠️ **উচ্চ:** ভারী বৃষ্টির দমকা হাওয়া (সর্বোচ্চ **{max_hourly} mm/h**) শহরাঞ্চলে রাস্তায় জলবদ্ধতা ও হঠাৎ বন্যার উচ্চ ঝুঁকি সৃষ্টি করে।",
            "MODERATE": "⚠️ **মাঝারি:** প্রতি ঘণ্টায় **{max_hourly} mm/h** বৃষ্টিপাতের ফলে রাস্তায় আংশিক জলাবদ্ধতা এবং ড্রেনবিহীন সংযোগস্থলে পানি জমতে পারে।",
            "LOW": "⚠️ **নগণ্য:** অতিবৃষ্টির কোনো সম্ভাবনা নেই। হঠাৎ বন্যা হওয়ার সম্ভাবনা খুবই কম।"
        },
        "river_statuses": {
            "EXTREME": "🌊 **গুরুতর:** নদীর পানি ধারণ ক্ষমতা অতিক্রম করবে এবং প্রবাহ {start_discharge} m³/s থেকে বৃদ্ধি পেয়ে **{peak_discharge} m³/s** হবে। নিচু এলাকায় বন্যা হওয়া প্রায় নিশ্চিত।",
            "HIGH": "🌊 **মাঝারি থেকে উচ্চ:** নদীর পানি প্রবাহ বৃদ্ধি পেয়ে **{peak_discharge} m³/s** ({multiplier}x বৃদ্ধি) এর শিখরে পৌঁছাবে। নদীর দুই কূল উপচে প্লাবিত হওয়ার সম্ভাবনা রয়েছে।",
            "MODERATE": "🌊 **কম থেকে মাঝারি:** নদীর পানি বৃদ্ধি পাবে তবে তা মূলত ধারণক্ষমতার মধ্যেই থাকবে (সর্বোচ্চ প্রবাহ: **{peak_discharge} m³/s**)।",
            "LOW": "🌊 **স্থিতিশীল:** নদীর পানি প্রবাহ স্বাভাবিক রয়েছে এবং নিরাপদ মাত্রায় প্রায় **{peak_discharge} m³/s** বজায় আছে।"
        },
        "river_statuses_fallback": {
            "EXTREME": "🌊 **উচ্চ:** স্থানীয় তীব্র বৃষ্টির পানির কারণে নালা এবং ছোট খালগুলিতে মারাত্মক জলাবদ্ধতা ও উপচে পড়ার আশঙ্কা রয়েছে।",
            "HIGH": "🌊 **মাঝারি:** স্থানীয় ড্রেন ও ছোট নালাগুলিতে পানির স্তর দ্রুত বৃদ্ধি পেতে পারে।",
            "MODERATE": "🌊 **কম:** ছোট নদী এবং খালগুলির পানির স্তর কিছুটা বাড়লেও তা সীমার মধ্যেই থাকবে।",
            "LOW": "🌊 **স্থিতিশীল:** নালা এবং খালের পানির স্তর ঋতুভিত্তিক স্বাভাবিক সীমার মধ্যেই রয়েছে।"
        },
        "soil_statuses": {
            "EXTREME": "🌱 **সম্পৃক্ত:** টানা {consecutive_days} দিন বৃষ্টিপাতের ফলে মাটি পুরোপুরি সম্পৃক্ত হয়ে যাওয়ায় আর পানি শোষণ করতে পারবে না, যার ফলে ৯০%+ বৃষ্টি সরাসরি নদী বা খালে গড়িয়ে পড়বে।",
            "HIGH": "🌱 **অত্যধিক ভেজা:** মাটিতে আর্দ্রতার পরিমাণ খুব বেশি। পানি শোষণের ক্ষমতা অনেকাংশে হ্রাস পাওয়ায় পানি নিষ্কাশন দ্রুত শুরু হবে।",
            "MODERATE": "🌱 **মাঝারি ভেজা:** মাটির পানি শোষণ ক্ষমতা মাঝারি, তবে সপ্তাহ জুড়ে আর্দ্রতার কারণে শোষণ ক্ষমতা ক্রমশ হ্রাস পাবে।",
            "LOW": "🌱 **শুষ্ক / শোষণক্ষম:** মাটির পানি শোষণ ক্ষমতা অনেক বেশি। বৃষ্টির পানি সরাসরি ভূগর্ভে চলে যাবে।"
        },
        "actions": {
            "EXTREME": [
                "**নিচু এলাকা থেকে দ্রুত সরে যান:** স্থানীয় কর্তৃপক্ষের নির্দেশনা অনুযায়ী অবিলম্বে নিরাপদ স্থানে আশ্রয় নিন। পালানোর রাস্তা বন্ধ হওয়া পর্যন্ত অপেক্ষা করবেন না।",
                "**চলমান পানি পাড়ি দেবেন না:** মাত্র ১৫ সেমি প্রবাহিত পানি আপনাকে ফেলে দিতে পারে এবং ৬০ সেমি পানি গাড়ি ভাসিয়ে নিয়ে যেতে পারে।",
                "**জরুরি কিট প্রস্তুত রাখুন:** প্রয়োজনীয় কাগজপত্র, শুকনো খাবার, বিশুদ্ধ পানি এবং পাওয়ার ব্যাংক হাতের কাছে রাখুন। মূল্যবান জিনিসপত্র ঘরের উপরে রাখুন।"
            ],
            "HIGH": [
                "**সর্বশেষ তথ্যে নজর রাখুন:** হঠাৎ বন্যা সতর্কতার জন্য স্থানীয় আবহাওয়া বুলেটিনগুলি নিয়মিত অনুসরণ করুন।",
                "**বাড়ির চারপাশ সুরক্ষিত করুন:** বাড়ির বাইরের আলগা জিনিসপত্র ভেতরে নিয়ে আসুন এবং ড্রেন ও নর্দমা পরিষ্কার রাখুন।",
                "**রাস্তা পরিকল্পনা করুন:** ভারী বৃষ্টির সময় নদীর পার্শ্ববর্তী রাস্তা এবং নিচু আন্ডারপাস দিয়ে যাতায়াত এড়িয়ে চলুন।"
            ],
            "MODERATE": [
                "**নর্দমা পরিষ্কার রাখুন:** বাড়ির ছাদের পাইপ এবং পানি নিষ্কাশন পথ পাতা বা ময়লামুক্ত রাখুন।",
                "**সাবধানে গাড়ি চালান:** বৃষ্টির সময় অত্যন্ত সতর্কতার সাথে গাড়ি চালান এবং গভীর জলাবদ্ধ রাস্তায় গাড়ি নামাবেন না।",
                "**জরুরি সরঞ্জাম পরীক্ষা করুন:** টর্চলাইট, ফার্স্ট এইড বক্স ইত্যাদি জরুরি জিনিসপত্র সহজে পাওয়ার মতো জায়গায় রাখুন।"
            ],
            "LOW": [
                "**কোনো তাৎক্ষণিক পদক্ষেপ নেই:** বর্তমানে বন্যা প্রতিরোধক কোনো পদক্ষেপের প্রয়োজন নেই।",
                "**নিয়মিত রক্ষণাবেক্ষণ:** আপনার বাড়ির ড্রেনেজ ব্যবস্থা নিয়মিত পরীক্ষা করতে থাকুন।"
            ]
        }
    }
}

def calculate_flood_risk(weather_data, flood_data, lang="en"):
    """
    Analyzes meteorological and hydrological telemetry to determine flood risk and outputs a translated report.
    
    Parameters:
    - weather_data: dict containing daily and hourly weather forecasts
    - flood_data: dict containing river discharge forecasts
    - lang: string target language ('en', 'es', 'hi', 'fr', 'bn')
    
    Returns:
    - dict: structured risk parameters and generated report.
    """
    daily = weather_data.get('daily', {})
    hourly = weather_data.get('hourly', {})
    
    daily_precip = daily.get('precipitation_sum', [0] * 7)
    hourly_precip = hourly.get('precipitation', [0] * 168)
    time_hourly = hourly.get('time', [])
    
    total_precip_7d = sum(daily_precip)
    max_daily_precip = max(daily_precip) if daily_precip else 0
    max_hourly_precip = max(hourly_precip) if hourly_precip else 0
    
    # Identify active rain hours and consecutive rainy days
    rainy_days_count = sum(1 for p in daily_precip if p >= 2.0)
    consecutive_rain_days = 0
    temp_consec = 0
    for p in daily_precip:
        if p >= 2.0:
            temp_consec += 1
            consecutive_rain_days = max(consecutive_rain_days, temp_consec)
        else:
            temp_consec = 0
            
    # Find peak rain time
    peak_rain_hour_idx = hourly_precip.index(max_hourly_precip) if max_hourly_precip > 0 else 0
    peak_rain_time = ""
    if time_hourly and peak_rain_hour_idx < len(time_hourly):
        raw_time = time_hourly[peak_rain_hour_idx]
        try:
            from datetime import datetime
            dt = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M")
            # Format time beautifully
            if lang in TRANSLATIONS:
                # We can translate weekday names or keep format structured
                peak_rain_time = dt.strftime("%Y-%m-%d %H:%M")
            else:
                peak_rain_time = dt.strftime("%A, %b %d at %H:%M")
        except Exception:
            peak_rain_time = raw_time

    # Hydrological Telemetry Extraction (River Discharge in m³/s)
    flood_daily = flood_data.get('daily', {})
    river_discharge = flood_daily.get('river_discharge', [])
    
    if not river_discharge or all(v is None for v in river_discharge):
        river_discharge = [0.0] * 7
        has_river_data = False
    else:
        river_discharge = [float(v) if v is not None else 0.0 for v in river_discharge]
        has_river_data = True
        
    start_discharge = river_discharge[0] if river_discharge else 0.0
    peak_discharge = max(river_discharge) if river_discharge else 0.0
    
    discharge_multiplier = 1.0
    if start_discharge > 0.1:
        discharge_multiplier = peak_discharge / start_discharge
    elif peak_discharge > 0.1:
        discharge_multiplier = 3.0
        
    # Multi-Factor Risk Assessment
    meteo_score = 0.0
    hydro_score = 0.0
    
    if max_hourly_precip > 25.0:
        meteo_score += 4.5
    elif max_hourly_precip > 10.0:
        meteo_score += 3.0
    elif max_hourly_precip > 5.0:
        meteo_score += 1.5
        
    if total_precip_7d > 150.0:
        meteo_score += 4.5
    elif total_precip_7d > 80.0:
        meteo_score += 3.5
    elif total_precip_7d > 40.0:
        meteo_score += 2.0
    elif total_precip_7d > 15.0:
        meteo_score += 1.0
        
    if consecutive_rain_days >= 5:
        meteo_score += 1.0
    elif consecutive_rain_days >= 3:
        meteo_score += 0.5
        
    if has_river_data:
        if discharge_multiplier >= 2.5:
            hydro_score += 4.0
        elif discharge_multiplier >= 1.8:
            hydro_score += 2.5
        elif discharge_multiplier >= 1.3:
            hydro_score += 1.2
            
        if peak_discharge > 250.0:
            hydro_score += 4.5
        elif peak_discharge > 80.0:
            hydro_score += 3.0
        elif peak_discharge > 20.0:
            hydro_score += 1.5
    else:
        hydro_score = meteo_score * 0.6
        
    combined_score = (meteo_score * 0.55) + (hydro_score * 0.45)
    combined_score = min(max(combined_score, 0.0), 10.0)
    
    # Categorize Risk
    if combined_score >= 7.5:
        risk_level = "EXTREME"
        risk_color = "danger-extreme"
        risk_icon = "🚨"
    elif combined_score >= 4.5:
        risk_level = "HIGH"
        risk_color = "danger-high"
        risk_icon = "⚠️"
    elif combined_score >= 2.0:
        risk_level = "MODERATE"
        risk_color = "danger-moderate"
        risk_icon = "⚡"
    else:
        risk_level = "LOW"
        risk_color = "danger-low"
        risk_icon = "✅"

    # Multi-language text mapping
    lang_key = lang.lower() if lang.lower() in TRANSLATIONS else "en"
    
    if lang_key == "en":
        risk_badge = f"{risk_level} Warning" if risk_level in ["EXTREME", "HIGH"] else f"{risk_level} Advisory" if risk_level == "MODERATE" else "Green Normal"
        summary_md = generate_summary_report_en(
            risk_level, risk_icon, combined_score,
            total_precip_7d, max_daily_precip, max_hourly_precip, peak_rain_time,
            start_discharge, peak_discharge, discharge_multiplier, has_river_data,
            consecutive_rain_days
        )
    else:
        dict_lang = TRANSLATIONS[lang_key]
        translated_level = {
            "EXTREME": "CRÍTICO" if lang_key == "es" else "अत्यंत" if lang_key == "hi" else "EXTRÊME" if lang_key == "fr" else "চরম",
            "HIGH": "ALTO" if lang_key == "es" else "उच्च" if lang_key == "hi" else "ÉLEVÉ" if lang_key == "fr" else "উচ্চ",
            "MODERATE": "MODERADO" if lang_key == "es" else "मध्यम" if lang_key == "hi" else "MODÉRÉ" if lang_key == "fr" else "মাঝারি",
            "LOW": "BAJO" if lang_key == "es" else "सामान्य" if lang_key == "hi" else "FAIBLE" if lang_key == "fr" else "নিম্ন"
        }.get(risk_level, risk_level)
        
        risk_badge = f"{risk_icon} {translated_level}"
        summary_md = generate_summary_report_translated(
            lang_key, risk_level, risk_icon, combined_score,
            total_precip_7d, max_daily_precip, max_hourly_precip, peak_rain_time,
            start_discharge, peak_discharge, discharge_multiplier, has_river_data,
            consecutive_rain_days
        )
    
    # 5. Extract active calamity alerts
    calamity_alert = None
    if combined_score >= 7.5:
        calamity_alert = {
            "es": "🚨 ALERTA ROJA DE INUNDACIÓN CATÁSTROFE: Se pronostica un desbordamiento grave de los ríos. Despeje las zonas bajas y siga las órdenes de evacuación.",
            "hi": "🚨 रेड अलर्ट - भीषण बाढ़ आपातकाल: नदियों में गंभीर जल-स्तर वृद्धि का अनुमान है। तुरंत निचले इलाकों से हटें और सुरक्षित स्थान पर जाएं।",
            "fr": "🚨 URGENCE ABSOLUE INONDATION : Crues majeures prévues. Évacuez les zones basses et suivez les instructions des services de secours.",
            "bn": "🚨 চরম লাল সতর্কতা - মহাবিপর্যয়কর বন্যা: নদীর পানি মারাত্মকভাবে উপচে পড়ার আশঙ্কা। অবিলম্বে নিচু এলাকা খালি করে নিরাপদ আশ্রয়ে যান।",
            "en": "🚨 RED FLOOD EMERGENCY CALAMITY: Severe out-of-bank river flow forecast. Evacuate low-lying regions immediately."
        }.get(lang_key, "🚨 RED FLOOD EMERGENCY CALAMITY: Evacuate low-lying regions immediately.")
    elif combined_score >= 4.5:
        calamity_alert = {
            "es": "⚠️ ALERTA DE RIESGO DE INUNDACIÓN: Fuertes lluvias acumuladas y escorrentías urbanas intensas. Monitoree canales y arroyos.",
            "hi": "⚠️ बाढ़ जोखिम चेतावनी: भारी वर्षा और तीव्र शहरी जलभराव की आशंका। स्थानीय नालों और नदियों के जल स्तर पर नजर रखें।",
            "fr": "⚠️ ALERTE INONDATION : Précipitations intenses et forts ruissellements urbains. Surveillez les cours d'eau.",
            "bn": "⚠️ বন্যা ঝুঁকি সতর্কতা: ভারী বৃষ্টিপাত এবং তীব্র জলাবদ্ধতার আশঙ্কা। খাল ও নদীর পানি বৃদ্ধির ওপর নজর রাখুন।",
            "en": "⚠️ HIGH FLOOD HAZARD WARNING: Torrential rainfall and rapid urban runoff expected. Monitor streams."
        }.get(lang_key, "⚠️ HIGH FLOOD HAZARD WARNING: Torrential rainfall and rapid urban runoff expected.")

    return {
        "risk_level": risk_level,
        "risk_score": round(combined_score, 1),
        "risk_color": risk_color,
        "risk_icon": risk_icon,
        "risk_badge": risk_badge,
        "calamity_alert": calamity_alert,
        "metrics": {
            "total_precip_7d": round(total_precip_7d, 1),
            "max_daily_precip": round(max_daily_precip, 1),
            "max_hourly_precip": round(max_hourly_precip, 1),
            "peak_rain_time": peak_rain_time,
            "start_discharge": round(start_discharge, 1) if has_river_data else None,
            "peak_discharge": round(peak_discharge, 1) if has_river_data else None,
            "discharge_multiplier": round(discharge_multiplier, 2) if has_river_data else None,
            "consecutive_rain_days": consecutive_rain_days
        },
        "summary_markdown": summary_md
    }

def generate_summary_report_en(risk_level, risk_icon, score, 
                               total_precip, max_daily, max_hourly, peak_rain_time,
                               start_discharge, peak_discharge, multiplier, has_river_data,
                               consecutive_days):
    """
    Generates English markdown early warning report.
    """
    if risk_level == "EXTREME":
        situation = f"**CRITICAL FLOOD EMERGENCY:** A severe combination of extreme rainfall ({total_precip}mm forecast over 7 days) and massive hydrological surge is imminent. River discharge is projected to rise to **{peak_discharge} m³/s** ({multiplier}x normal levels). Immediate action is required to protect life and property."
        flash_flood_status = f"⚠️ **CRITICAL:** High-intensity hourly precipitation (peaking at **{max_hourly} mm/h**) will overwhelm urban storm drainage within minutes of onset, creating widespread torrential flash floods."
        river_flood_status = f"🌊 **CRITICAL:** River channel capacity will be exceeded as discharge escalates from {start_discharge} m³/s to **{peak_discharge} m³/s**. Out-of-bank flooding in low-lying zones is virtually certain." if has_river_data else "🌊 **HIGH:** Heavy localized runoff is expected to cause severe creek and drainage overflow due to intense surface discharge."
        soil_status = f"🌱 **SATURATED:** Saturated soil matrices from {consecutive_days} consecutive days of rain will prevent absorption, driving 90%+ of rainfall directly into surface runoff."
        actions = [
            "**EVACUATE LOW-LYING AREAS:** If instructed by local officials, evacuate immediately. Do not wait until flooding blocks exit paths.",
            "**NEVER CROSS FLOODWATERS:** As little as 15cm (6 inches) of moving water can knock you off your feet, and 60cm (2 feet) can sweep vehicles away.",
            "**ASSEMBLE EMERGENCY KIT:** Keep documents, dry food, clean water, and power banks ready. Move valuables to the highest level of your home."
        ]
    elif risk_level == "HIGH":
        situation = f"**HIGH RISK ALERT:** Meteorological indicators show a substantial flood risk. Expected total precipitation is **{total_precip} mm** with a maximum daily downpour of **{max_daily} mm**. Runoff channels are expected to experience heavy load."
        flash_flood_status = f"⚠️ **HIGH:** Heavy bursts of rain (up to **{max_hourly} mm/h**) pose a high threat of street flooding, underpass inundation, and localized flash flooding in urban areas."
        river_flood_status = f"🌊 **MODERATE TO HIGH:** River discharge peaks at **{peak_discharge} m³/s** (representing a {multiplier}x increase). Some minor-to-moderate riverbank overflow is likely." if has_river_data else "🌊 **MODERATE:** Localized pooling and rapid rise in small channels and streams is expected."
        soil_status = f"🌱 **HEAVILY WET:** High soil moisture content. Absorption capacity is significantly diminished, leading to rapid runoff onset."
        actions = [
            "**MONITOR UPDATES:** Stay tuned to NOAA/Local weather service broadcasts for live flash flood warnings.",
            "**SECURE OUTDOORS:** Move outdoor items inside and verify sump pump and gutters are clear.",
            "**PLAN ROUTES:** Avoid low-lying underpasses and roads adjacent to rivers or canals during peak rain."
        ]
    elif risk_level == "MODERATE":
        situation = f"**MODERATE ADVISORY:** Active weather patterns will bring standard-to-heavy rains totaling **{total_precip} mm** over the week. While general flooding is not expected, localized drainage issues may occur."
        flash_flood_status = f"⚠️ **MODERATE:** Hourly precipitation of **{max_hourly} mm/h** may cause minor street flooding and pooling in poorly-drained intersections."
        river_flood_status = f"🌊 **LOW TO MODERATE:** River channels will rise but are expected to remain mostly within containment basins (peak discharge: **{peak_discharge} m³/s**)." if has_river_data else "🌊 **LOW:** Local creeks and channels will see rising levels but stay within banks."
        soil_status = "🌱 **MODERATELY DAMP:** Soil has moderate capacity to absorb rainfall, but persistent dampness will decrease absorption towards the end of the week."
        actions = [
            "**CLEAN GUTTERS:** Ensure household gutters and downspouts are clear of leaves and debris.",
            "**EXERCISE CAUTION:** Drive carefully in rainy periods and avoid driving through deep standing water.",
            "**CHECK SUPPLIES:** Ensure basic emergency supplies (flashlights, first aid) are accessible."
        ]
    else:
        situation = f"**NORMAL CONDITIONS:** The meteorology forecast indicates dry or very light rain conditions ({total_precip}mm cumulative). Hydrological metrics remain stable and within safe limits."
        flash_flood_status = "⚠️ **NEGLIGIBLE:** No high-intensity rainfall events are projected. Flash flooding is highly unlikely."
        river_flood_status = f"🌊 **STABLE:** River flow is normal, resting safely around **{peak_discharge} m³/s**." if has_river_data else "🌊 **STABLE:** Stream and channel levels are at baseline seasonal levels."
        soil_status = "🌱 **DRY / RECEPTIVE:** Land displays high absorption potential. Rain will soak directly into aquifers and soils."
        actions = [
            "**NO IMMEDIATE ACTIONS:** No flood protection measures are currently needed.",
            "**ROUTINE MAINTENANCE:** Perform regular checks on drainage channels and home roofs."
        ]

    actions_list = "\n".join([f"- {action}" for action in actions])
    
    return f"""### {risk_icon} Flood Assessment: {risk_level} (Threat Score: {score:.1f}/10)

{situation}

---

#### 📊 Telemetry Diagnostics

| Measurement | Current Value | Threshold Status |
| :--- | :--- | :--- |
| **7-Day Cumulative Rainfall** | {total_precip} mm | {"Excessive" if total_precip > 80 else "Elevated" if total_precip > 40 else "Normal"} |
| **Peak 24h Rainfall** | {max_daily} mm | {"Heavy" if max_daily > 30 else "Moderate" if max_daily > 10 else "Light"} |
| **Max Hourly Intensity** | {max_hourly} mm/h | {"Torrid" if max_hourly > 15 else "Heavy" if max_hourly > 5 else "Light"} |
| **Peak River Discharge** | {f"{peak_discharge} m³/s" if has_river_data else "N/A"} | {f"{multiplier:.2f}x Baseline Surge" if has_river_data else "No River Near Sensor"} |
| **Consecutive Wet Days** | {consecutive_days} days | {"Saturated Soil" if consecutive_days >= 4 else "Damp Soil" if consecutive_days >= 2 else "Receptive Soil"} |

*Heaviest precipitation event is anticipated on **{peak_rain_time if peak_rain_time else "N/A"}**.*

---

#### 🔬 Threat Analysis Breakdown

* **Flash Flooding Potential**
  {flash_flood_status}

* **Riverine / Channel Overspill**
  {river_flood_status}

* **Soil Saturation & Runoff Velocity**
  {soil_status}

---

#### 🛡️ Required Safety Protocols

{actions_list}
"""

def generate_summary_report_translated(lang, risk_level, risk_icon, score, 
                                       total_precip, max_daily, max_hourly, peak_rain_time,
                                       start_discharge, peak_discharge, multiplier, has_river_data,
                                       consecutive_days):
    """
    Generates translated markdown early warning reports (es, hi, fr, bn).
    """
    d = TRANSLATIONS[lang]
    
    # 1. Translate situation
    situation_raw = d["situations"].get(risk_level, d["situations"]["LOW"])
    situation = situation_raw.format(
        total_precip=total_precip,
        max_daily=max_daily,
        peak_discharge=peak_discharge,
        multiplier=f"{multiplier:.2f}"
    )
    
    # 2. Translate threat breakdowns
    flash_raw = d["flash_statuses"].get(risk_level, d["flash_statuses"]["LOW"])
    flash_flood_status = flash_raw.format(max_hourly=max_hourly)
    
    if has_river_data:
        river_raw = d["river_statuses"].get(risk_level, d["river_statuses"]["LOW"])
        river_flood_status = river_raw.format(
            start_discharge=start_discharge,
            peak_discharge=peak_discharge,
            multiplier=f"{multiplier:.2f}"
        )
    else:
        river_raw = d["river_statuses_fallback"].get(risk_level, d["river_statuses_fallback"]["LOW"])
        river_flood_status = river_raw
        
    soil_raw = d["soil_statuses"].get(risk_level, d["soil_statuses"]["LOW"])
    soil_status = soil_raw.format(consecutive_days=consecutive_days)
    
    # 3. Actions list
    actions_raw = d["actions"].get(risk_level, d["actions"]["LOW"])
    actions_list = "\n".join([f"- {action}" for action in actions_raw])
    
    # 4. Determine metric states
    state_7d = d["status_excessive"] if total_precip > 80 else d["status_elevated"] if total_precip > 40 else d["status_normal"]
    state_24h = d["status_heavy"] if max_daily > 30 else d["status_moderate"] if max_daily > 10 else d["status_light"]
    state_intensity = d["status_torrid"] if max_hourly > 15 else d["status_heavy"] if max_hourly > 5 else d["status_light"]
    state_discharge = f"{multiplier:.2f}x {d['status_surge']}" if has_river_data else d["status_no_sensor"]
    state_soil = d["status_saturated"] if consecutive_days >= 4 else d["status_damp"] if consecutive_days >= 2 else d["status_receptive"]
    
    translated_risk_title = {
        "EXTREME": "CRÍTICO" if lang == "es" else "अत्यंत" if lang == "hi" else "CRITIQUE" if lang == "fr" else "চরম",
        "HIGH": "ALTO" if lang == "es" else "उच्च" if lang == "hi" else "ÉLEVÉ" if lang == "fr" else "উচ্চ",
        "MODERATE": "MODERADO" if lang == "es" else "मध्यમ" if lang == "hi" else "MODÉRÉ" if lang == "fr" else "মাঝারি",
        "LOW": "BAJO" if lang == "es" else "सामान्य" if lang == "hi" else "FAIBLE" if lang == "fr" else "নিম্ন"
    }.get(risk_level, risk_level)

    return f"""### {risk_icon} {d['title']}: {translated_risk_title} ({d['score_label']}: {score:.1f}/10)

{situation}

---

#### 📊 {d['telemetry_title']}

| {d['col_measure']} | {d['col_val']} | {d['col_status']} |
| :--- | :--- | :--- |
| **{d['metric_7d']}** | {total_precip} mm | {state_7d} |
| **{d['metric_peak24h']}** | {max_daily} mm | {state_24h} |
| **{d['metric_intensity']}** | {max_hourly} mm/h | {state_intensity} |
| **{d['metric_discharge']}** | {f"{peak_discharge} m³/s" if has_river_data else "N/A"} | {state_discharge} |
| **{d['metric_consec']}** | {consecutive_days} | {state_soil} |

*{d['peak_time_msg']} **{peak_rain_time if peak_rain_time else "N/A"}**.*

---

#### 🔬 {d['threat_analysis_title']}

* **{d['threat_flash']}**
  {flash_flood_status}

* **{d['threat_river']}**
  {river_flood_status}

* **{d['threat_soil']}**
  {soil_status}

---

#### 🛡️ {d['safety_protocols_title']}

{actions_list}
"""
