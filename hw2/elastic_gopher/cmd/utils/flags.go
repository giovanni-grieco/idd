package utils

import (
	"errors"
	"strings"
)

func FlagParser(flagValues string) (map[string]string, error) {
	var resultMap map[string]string
	resultMap = make(map[string]string)
	kvs := strings.Split(flagValues, ",")
	for _, kv := range kvs {
		kv = strings.TrimSpace(kv)
		kvArr := strings.SplitN(kv, "=", 2)
		if len(kvArr) != 2 {
			return nil, errors.New("invalid flag value")
		}
		resultMap[kvArr[0]] = kvArr[1]
	}
	return resultMap, nil
}
