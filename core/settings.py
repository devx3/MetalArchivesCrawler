BOT_NAME = 'metal-archives-scrapper'

SPIDER_MODULES = ['core.spiders']
NEWSPIDER_MODULE = 'core.spiders'

# USER_AGENT = 'core (+http://www.yourdomain.com)'

ROBOTSTXT_OBEY = True

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

ITEM_PIPELINES = {
    'core.pipelines.MetalArchivesMongoDB': 400,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPLASH_URL = 'http://localhost:8050/'

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# MONGO DB
MONGO_URI = 'mongodb://localhost'
MONGO_DB = 'metal_archives'
