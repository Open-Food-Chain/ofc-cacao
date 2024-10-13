# blocknotify-data-agnostic
expects 1 unqiue data field, that either starts with unique- or has an object in the field that looks like this {"unique":True, "value":[the actual value]}

in the same way you can also instruct it to hash or dubble hash a field with 
{"hash":True, "value":[the actual value]}
{"double_hash":True, "value":[the actual value]}

in which case it will hash or dubble hash the data in that field.
Only the value part will be put on chain. 