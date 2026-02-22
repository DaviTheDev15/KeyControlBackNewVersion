#!/bin/sh

SOLR_HOST="solr"
SOLR_PORT="8983"
CORE_NAME="key-control-core"

echo "Aguardando Solr iniciar..."
until curl -s "http://$SOLR_HOST:$SOLR_PORT/solr/admin/cores?action=STATUS&core=$CORE_NAME" | grep -q "\"instanceDir\""; do
  echo "Solr ainda não está pronto ou core $CORE_NAME não criado. Tentando novamente em 2s..."
  sleep 2
done

echo "Solr e Core detectados! Configurando Schema..."

SCHEMA_API="http://$SOLR_HOST:$SOLR_PORT/solr/$CORE_NAME/schema"

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{ "name":"responsavel_nome", "type":"text_pt", "stored":true, "indexed":true }
}' $SCHEMA_API

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{ "name":"responsavel_cpf", "type":"string", "stored":true, "indexed":true }
}' $SCHEMA_API

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{ "name":"responsavel_siap", "type":"string", "stored":true, "indexed":true }
}' $SCHEMA_API

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{ "name":"ativo", "type":"boolean", "stored":true, "indexed":true }
}' $SCHEMA_API

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{ "name":"responsavel_id", "type":"pint", "stored":true, "indexed":true }
}' $SCHEMA_API

curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{ "name":"responsavel_data_nascimento", "type":"pdate", "stored":true, "indexed":true }
}' $SCHEMA_API

echo "Configuração do Schema concluída com sucesso!"