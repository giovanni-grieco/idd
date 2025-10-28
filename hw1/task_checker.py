import logging

logger = logging.getLogger("wrapper")


def check_task(task: dict) -> bool:
    try:
        # Verifica presenza del campo "schema"
        if "schema" not in task:
            logger.error("Missing 'schema' field in task")
            return False
        
        schema = task["schema"]
        if not isinstance(schema, list) or len(schema) == 0:
            logger.error("'schema' must be a non-empty list")
            return False
        
        schema_length = len(schema)
        logger.info(f"Schema has {schema_length} fields: {schema}")
        
        # Verifica ogni dominio/sito (escludendo "schema")
        domains = [key for key in task.keys() if key != "schema"]
        
        if len(domains) == 0:
            logger.error("No domains found in task")
            return False
        
        for domain in domains:
            domain_config = task[domain]
            
            # Verifica presenza di "xpaths"
            if "xpaths" not in domain_config:
                logger.error(f"Missing 'xpaths' field for domain: {domain}")
                return False
            
            xpaths = domain_config["xpaths"]
            if not isinstance(xpaths, list):
                logger.error(f"'xpaths' must be a list for domain: {domain}")
                return False
            
            # Verifica che la lunghezza di xpaths corrisponda alla lunghezza dello schema
            if len(xpaths) != schema_length:
                logger.error(f"Domain '{domain}': xpaths length ({len(xpaths)}) doesn't match schema length ({schema_length})")
                return False
            
            # Verifica che ogni elemento di xpaths sia un array con almeno un elemento
            for i, xpath_array in enumerate(xpaths):
                if not isinstance(xpath_array, list) or len(xpath_array) == 0:
                    logger.error(f"Domain '{domain}': xpath for field '{schema[i]}' must be a non-empty list")
                    return False
                
                # Verifica che ogni xpath sia una stringa non vuota
                for j, xpath in enumerate(xpath_array):
                    if not isinstance(xpath, str):
                        logger.error(f"Domain '{domain}': xpath {j} for field '{schema[i]}' must be a non-empty string")
                        return False
            
            # Verifica presenza di "pages"
            if "pages" not in domain_config:
                logger.error(f"Missing 'pages' field for domain: {domain}")
                return False
            
            pages = domain_config["pages"]
            if not isinstance(pages, list) or len(pages) == 0:
                logger.error(f"'pages' must be a non-empty list for domain: {domain}")
                return False
            
            # Verifica che ogni page sia una stringa non vuota
            for page in pages:
                if not isinstance(page, str) or page.strip() == "":
                    logger.error(f"Domain '{domain}': each page must be a non-empty string")
                    return False
            
            logger.info(f"Domain '{domain}' validated successfully: {len(pages)} pages, {len(xpaths)} xpath groups")
        
        logger.info("Task validation completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during task validation: {str(e)}")
        return False