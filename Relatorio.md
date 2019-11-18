
## Relaório Técnico

### ZMQ
- Abstração da programação direta com sockets;
- Sem necessidade de uma persistência visto que o programa é feito para um cluster;
- Padrão **publish & subscribe** para mensagens globais de controle utilizadas;
  - Ex: Comando para inicar quebra de arquivo, comando para parar quebra de arquivo;
- Padrão **request & reply** para mensagens únicas entre mestre e escravo;
  - Ex: Anunciamento na rede, envio de status, envio de notificação, envio de configuração;

### Funcionamento

#### Mestre
- Abre um socket TCP na porta 5561 com contexto Publisher para a comunicação publish & subscribe;
- Abre um socket TCP na porta 5562 com contexto para a comunicação request & reply;
- Inicia thread para tratamento das mensagens request & reply;
- Inicia loop de interface com o usuário para envio de mensagens globais e visualização de status na thread principal;

#### Escravo
- Conecta no socket TCP na porta 5561 do mestre com contexto Subscriber para a comunicação publish & subscribe;
- Se increve em todas as mensagens do mestre.
- Conecta no socket TCP na porta 5562 do mestre com contexto Request para a comunicação request & reply;
- Inicia thread para envio de status periódicos ao mestre.
- Inicia loop para recebimento de mensagens globais do mestre na thread principal.
- Quando recebido um comando para quebra de arquivo inicia uma thread para tal que acabará quando o arquivo for quebrado ou quando receber um comando para cancelar do mestre.
