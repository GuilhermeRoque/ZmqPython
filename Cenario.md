
## Cenário
### Mestre
- Instalar o especificado em "requirements.txt";
- Se foi criado um Virtual Enviroment, ativá-lo;
- Para comunicação é utilizado sockets TCP com as portas 5561 e 5562, necessário ter as mesmas disponíveis.
- Executar o script "publisher.py" com o comando: **python3 publisher.py**
- Esperar os escravos conectarem. Estes podem ser vistos através do comando '1' da lista de opções inicial apresentada;
- Enviar o arquivo para quebra de senhas através do comando '2' da lista de opções inicial apresentada, e posteriormente inserindo o caminho absoluto do arquivo Ex: "/home/usuario/arquivo.txt;
- Quando um dos escravos terminar o trabalho será exbida uma mensagem na tela ""Arquivo de senha  arquivo.txt  quebrado!"

### Escravos
- Instalar "john".
- Copiar o arquivo [john.conf](https://github.com/STD29006-classroom/2019-02-projeto-pratico-01-GuilhermeRoque/blob/master/john.conf) para a pasta .john que por padrão está no diretório do usuário (Ex: /home/user). 
- Instalar o especificado em "requirements.txt";
- Se foi criado um Virtual Enviroment, ativá-lo;
- Inserir o endereço IP do mestre;
- Executar o script "publisher.py" com o comando: **python3 subscriber.py**
