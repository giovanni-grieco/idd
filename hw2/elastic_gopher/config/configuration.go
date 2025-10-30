package config

type Config struct {
	ElasticsearchURL string
}

func LoadConfig() *Config {
	return &Config{
		ElasticsearchURL: "http://localhost:9200",
	}
}
