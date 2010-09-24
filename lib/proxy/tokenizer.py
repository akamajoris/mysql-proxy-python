
import mysql.tokenizer as tokenizer

#--
#- normalize a query
#-
#- * remove comments
#- * quote literals
#- * turn constants into ?
#- * turn tokens into uppercase
#-
#- @param tokens a array of tokens
#- @return normalized SQL query
#- 
#- @see tokenize
def normalize(tokens):
    #- we use a string-stack here and join them at the 
    #- see http://www.lua.org/pil/11.6.html for more
    #-
    stack = []
    #- literals that are SQL commands if they appear at the start
    #- (all uppercase)
    literal_keywords = {
        "COMMIT" : (),
        "ROLLBACK" : (),
        "BEGIN" : (),
        "START" : ("TRANSACTION", ),
    }

    for token in tokens:
        #- normalize the query
        if token.token_name == 'TK_COMMENT':
            pass
        elif token.token_name == 'TK_COMMENT_MYSQL':
            #- a /*!... */ comment
            #-
            #- we can't look into the comment as we don't know which server-version
            #- we will talk to, pass it on verbatimly
            stack.append("/*!" + token.text + "*/ ")
        elif token.token_name == "TK_LITERAL":
            if token.text.startswith('@'):
                #- app session variables as is
                stack.append(token.text + ' ')
            elif len(stack) == 0: #- nothing is on the stack yet
                u_text = token.text.upper()

                if literal_keywords.has_key(u_text):
                    stack.append(u_text + ' ')
                else:
                    stack.append('`' + token.text + '` ')

            elif len(stack) == 1:
                u_text = token.text.upper()

                starting_keyword = stack[0][:-1]

                if literal_keywords.has_key(starting_keyword) and\
                   literal_keywords[starting_keyword][0] == u_text:
                    stack.append(u_text + ' ')
                else:
                    stack.append('`' + token.text + '` ')
            else:
                stack.append("`" + token.text + "` ")
        elif token.token_name in ("TK_STRING", "TK_INTEGER", "TK_FLOAT"):
            stack.append('? ')
        elif token.token_name == "TK_FUNCTION":
            stack.append(token.text.upper())
        else:
            stack.append(token.text.upper() + ' ')

    return ''.join(stack)


#--
#- call the included tokenizer
#-
#- this def is only a wrapper and exists mostly
#- for constancy and documentation reasons
def tokenize(packet):
    return tokenizer.tokenize(packet)


#--
#- return the first command token
#-
#- * strips the leading comments
def first_stmt_token(tokens):
    for token in tokens:
        #- normalize the query
        if not token.token_name == "TK_COMMENT":
            #- commit and rollback at LITERALS
            return token
    return None


#--
#-[[
   #returns an array of simple token values
   #without id and name, and stripping all comments
   #@param tokens an array of tokens, as produced by the tokenize() def
   #@param quote_strings : if set, the string tokens will be quoted
   #@see tokenize
#-]]
def bare_tokens (tokens, quote_strings):
    simple_tokens = []
    for token in tokens:
        print '-' * 50, token
        if token.token_name == 'TK_STRING' and quote_strings:
            simple_tokens.append(token.text)
        elif token.token_name != 'TK_COMMENT':
            simple_tokens.append(token.text)
    return simple_tokens


#--
#-[[
    
   #Returns a text query from an array of tokens, stripping off comments
  
   #@param tokens an array of tokens, as produced by the tokenize() def
   #@param start_item ignores tokens before this one
   #@param _item ignores token after this one
   #@see tokenize
#-]]
def tokens_to_query ( tokens , start_item=None, _item=None):
    if start_item is None:
        start_item = 0

    if _item is None:
        _item = len(tokens)

    counter  = 0
    new_query = ''
    for token in tokens:
        counter += 1
        if counter >= start_item and counter <= _item:
            if (token.token_name == 'TK_STRING'):
                new_query += '"%s"' % token.text
            elif token.token_name != 'TK_COMMENT':
                new_query += token.text

            if token.token_name != 'TK_FUNCTION' and token.token_name != 'TK_COMMENT':
                new_query += ' '

    return new_query


#--
#-[[
   #returns an array of tokens, stripping off all comments

   #@param tokens an array of tokens, as produced by the tokenize() def
   #@see tokenize, simple_tokens
#-]]
def tokens_without_comments(tokens):
    new_tokens = []
    for token in tokens:
        if token.token_name != 'TK_COMMENT':
            new_tokens.append(token)
    return new_tokens
