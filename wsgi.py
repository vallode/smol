from smol import APP
import config

if __name__ == "__main__":
    APP.config.from_object(config.ProductionConfig)
    APP.run()
