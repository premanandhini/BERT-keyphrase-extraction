"""Evaluate the model"""

import argparse
import random
import logging
import os

import numpy as np
import torch

#from pytorch_pretrained_bert import BertForTokenClassification, BertConfig
from transformers import BertTokenizer, BertModel
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained("bert-base-uncased")
text=''' Search APIs

Most search APIs are multi-index, with the exception of the Explain API endpoints.

Routing

When executing a search, Elasticsearch will pick the "best" copy of the data based on the adaptive replica selection formula. Which shards will be searched on can also be controlled by providing the routing parameter. For example, when indexing tweets, the routing value can be the user name:

In such a case, if we want to search only on the tweets for a specific user, we can specify it as the routing, resulting in the search hitting only the relevant shard:

The routing parameter can be multi valued represented as a comma separated string. This will result in hitting the relevant shards where the routing values match to.

Adaptive Replica Selection

By default, Elasticsearch will use what is called adaptive replica selection. This allows the coordinating node to send the request to the copy deemed "best" based on a number of criteria:

 Response time of past requests between the coordinating node and the node containing the copy of the data 

 Time past search requests took to execute on the node containing the data 

 The queue size of the search threadpool on the node containing the data 

This can be turned off by changing the dynamic cluster setting cluster.routing.use_adaptive_replica_selection from true to false:

If adaptive replica selection is turned off, searches are sent to the index/indices shards in a round robin fashion between all copies of the data (primaries and replicas).

Stats Groups

A search can be associated with stats groups, which maintains a statistics aggregation per group. It can later be retrieved using the indices stats API specifically. For example, here is a search body request that associate the request with two different groups:

Global Search Timeout

Individual searches can have a timeout as part of the Request Body Search. Since search requests can originate from many sources, Elasticsearch has a dynamic cluster-level setting for a global search timeout that applies to all search requests that do not set a timeout in the request body. These requests will be cancelled after the specified time using the mechanism described in the following section on Search Cancellation

. Therefore the same caveats about timeout responsiveness apply.

The setting key is search.default_search_timeout and can be set using the Cluster Update Settings endpoints. The default value is no global timeout. Setting this value to -1 resets the global search timeout to no timeout.

Search Cancellation

Searches can be cancelled using standard task cancellation mechanism. By default, a running search only checks if it is cancelled or not on segment boundaries, therefore the cancellation can be delayed by large segments. The search cancellation responsiveness can be improved by setting the dynamic cluster-level setting search.low_level_cancellation to true. However, it comes with an additional overhead of more frequent cancellation checks that can be noticeable on large fast running search queries. Changing this setting only affects the searches that start after the change is made.

Search concurrency and parallelism

By default Elasticsearch doesnb t reject any search requests based on the number of shards the request hits. While Elasticsearch will optimize the search execution on the coordinating node a large number of shards can have a significant impact CPU and memory wise. It is usually a better idea to organize data in such a way that there are fewer larger shards. In case you would like to configure a soft limit, you can update the action.search.shard_count.limit cluster setting in order to reject search requests that hit too many shards.

The request parameter max_concurrent_shard_requests can be used to control the maximum number of concurrent shard requests the search API will execute for the request. This parameter should be used to protect a single request from overloading a cluster (e.g., a default request will hit all indices in a cluster which could cause shard request rejections if the number of shards per node is high). This default is based on the number of data nodes in the cluster but at most 256.

Search

The search API allows you to execute a search query and get back search hits that match the query. The query can either be provided using a simple query string as a parameter, or using a request body.

Multi-Index

All search APIs can be applied across multiple indices with support for the multi index syntax. For example, we can search on all documents within the twitter index:

We can also search all documents with a certain tag across several indices (for example, when there is one index per user):

Or we can search across all available indices using _all:

URI Search

A search request can be executed purely using a URI by providing request parameters. Not all search options are exposed when executing a search using this mode, but it can be handy for quick "curl tests". Here is an example:

And here is a sample response:

Parameters

The parameters allowed in the URI are:

Name Descriptionq

The query string (maps to the query_string query, see Query String Query for more details).

df

The default field to use when no field prefix is defined within the query.

analyzer

The analyzer name to be used when analyzing the query string.

analyze_wildcard

Should wildcard and prefix queries be analyzed or not. Defaults to false.

batched_reduce_size

The number of shard results that should be reduced at once on the coordinating node. This value should be used as a protection mechanism to reduce the memory overhead per search request if the potential number of shards in the request can be large.

default_operator

The default operator to be used, can be AND or OR. Defaults to OR.

lenient

If set to true will cause format based failures (like providing text to a numeric field) to be ignored. Defaults to false.

explain

For each hit, contain an explanation of how scoring of the hits was computed.

_source

Set to false to disable retrieval of the _source field. You can also retrieve part of the document by using _source_includes & _source_excludes (see the request body documentation for more details)

stored_fields

The selective stored fields of the document to return for each hit, comma delimited. Not specifying any value will cause no fields to return.

sort

Sorting to perform. Can either be in the form of fieldName, or fieldName:asc/fieldName:desc. The fieldName can either be an actual field within the document, or the special _score name to indicate sorting based on scores. There can be several sort parameters (order is important).

track_scores

When sorting, set to true in order to still track scores and return them as part of each hit.

track_total_hits

Defaults to 10,000. Set to false in order to disable the tracking of the total number of hits that match the query. It also accepts an integer which in this case represents the number of hits to count accurately. (See the request body documentation for more details).

timeout

A search timeout, bounding the search request to be executed within the specified time value and bail with the hits accumulated up to that point when expired. Defaults to no timeout.

terminate_after

The maximum number of documents to collect for each shard, upon reaching which the query execution will terminate early. If set, the response will have a boolean field terminated_early to indicate whether the query execution has actually terminated_early. Defaults to no terminate_after.

from

The starting from index of the hits to return. Defaults to 0.

size

The number of hits to return. Defaults to 10.

search_type

The type of the search operation to perform. Can be dfs_query_then_fetch or query_then_fetch. Defaults to query_then_fetch. See Search Type for more details on the different types of search that can be performed.

allow_partial_search_results

Set to false to return an overall failure if the request would produce partial results. Defaults to true, which will allow partial results in the case of timeouts or partial failures. This default can be controlled using the cluster-level setting search.default_allow_partial_results.

Request Body Search

The search request can be executed with a search DSL, which includes the Query DSL, within its body. Here is an example:

And here is a sample response:

Parameters

  timeout 

   A search timeout, bounding the search request to be executed within the specified time value and bail with the hits accumulated up to that point when expired. Search requests are canceled after the timeout is reached using the Search Cancellation

 mechanism. Defaults to no timeout. See Time units

. 

   from 

   To retrieve hits from a certain offset. Defaults to 0. 

   size 

   The number of hits to return. Defaults to 10. If you do not care about getting some hits back but only about the number of matches and/or aggregations, setting the value to 0 will help performance. 

   search_type 

   The type of the search operation to perform. Can be dfs_query_then_fetch or query_then_fetch. Defaults to query_then_fetch. See Search Type for more. 

   request_cache 

   Set to true or false to enable or disable the caching of search results for requests where size is 0, ie aggregations and suggestions (no top hits returned). See Shard request cache. 

   allow_partial_search_results 

   Set to false to return an overall failure if the request would produce partial results. Defaults to true, which will allow partial results in the case of timeouts or partial failures. This default can be controlled using the cluster-level setting search.default_allow_partial_results. 

   terminate_after 

   The maximum number of documents to collect for each shard, upon reaching which the query execution will terminate early. If set, the response will have a boolean field terminated_early to indicate whether the query execution has actually terminated_early. Defaults to no terminate_after. 

   batched_reduce_size 

   The number of shard results that should be reduced at once on the coordinating node. This value should be used as a protection mechanism to reduce the memory overhead per search request if the potential number of shards in the request can be large. 

   ccs_minimize_roundtrips 

   Defaults to true. Set to false to disable minimizing network round-trips between the coordinating node and the remote clusters when executing cross-cluster search requests. See Cross-cluster search reduction phase

 for more. 

 Out of the above, the search_type, request_cache and the allow_partial_search_results settings must be passed as query-string parameters. The rest of the search request should be passed within the body itself. The body content can also be passed as a REST parameter named source.

Both HTTP GET and HTTP POST can be used to execute search with body. Since not all clients support GET with body, POST is allowed as well.

Fast check for any matching docs

terminate_after is always applied after the post_filter and stops the query as well as the aggregation executions when enough hits have been collected on the shard. Though the doc count on aggregations may not reflect the hits.total in the response since aggregations are applied before the post filtering.

In case we only want to know if there are any documents matching a specific query, we can set the size to 0 to indicate that we are not interested in the search results. Also we can set terminate_after to 1 to indicate that the query execution can be terminated whenever the first matching document was found (per shard).

The response will not contain any hits as the size was set to 0. The hits.total will be either equal to 0, indicating that there were no matching documents, or greater than 0 meaning that there were at least as many documents matching the query when it was early terminated. Also if the query was terminated early, the terminated_early flag will be set to true in the response.

The took time in the response contains the milliseconds that this request took for processing, beginning quickly after the node received the query, up until all search related work is done and before the above JSON is returned to the client. This means it includes the time spent waiting in thread pools, executing a distributed search across the whole cluster and gathering all the results.

Doc value Fields

Allows to return the doc value representation of a field for each hit, for example:

 

 the name of the field 

 

 an object notation is supported as well 

 

 the object notation allows to specify a custom format 

Doc value fields can work on fields that have doc-values enabled, regardless of whether they are stored

* can be used as a wild card, for example:

 

 Match all fields ending with field 

 

 Format to be applied to all matching fields. 

Note that if the fields parameter specifies fields without docvalues it will try to load the value from the fielddata cache causing the terms for that field to be loaded to memory (cached), which will result in more memory consumption.

Custom formats

While most fields do not support custom formats, some of them do:

 Date fields can take any date format. 

 Numeric fields accept a DecimalFormat pattern. 

By default fields are formatted based on a sensible configuration that depends on their mappings: long, double and other numeric fields are formatted as numbers, keyword fields are formatted as strings, date fields are formatted with the configured date format, etc.

Explain

Enables explanation for each hit on how its score was computed.

Field Collapsing

Allows to collapse search results based on field values. The collapsing is done by selecting only the top sorted document per collapse key. For instance the query below retrieves the best tweet for each user and sorts them by number of likes.

 

 collapse the result set using the "user" field 

 

 sort the top docs by number of likes 

 

 define the offset of the first collapsed result 

The total number of hits in the response indicates the number of matching documents without collapsing. The total number of distinct group is unknown.

The field used for collapsing must be a single valued keyword or numeric field with doc_values activated

The collapsing is applied to the top hits only and does not affect aggregations.

Expand collapse results

It is also possible to expand each collapsed top hits with the inner_hits option.

 

 collapse the result set using the "user" field 

 

 the name used for the inner hit section in the response 

 

 the number of inner_hits to retrieve per collapse key 

 

 how to sort the document inside each group 

 

 the number of concurrent requests allowed to retrieve the inner_hits` per group 

See inner hits for the complete list of supported options and the format of the response.

It is also possible to request multiple inner_hits for each collapsed hit. This can be useful when you want to get multiple representations of the collapsed hits.

 

 collapse the result set using the "user" field 

 

 return the three most liked tweets for the user 

 

 return the three most recent tweets for the user 

The expansion of the group is done by sending an additional query for each inner_hit request for each collapsed hit returned in the response. This can significantly slow things down if you have too many groups and/or inner_hit requests.

The max_concurrent_group_searches request parameter can be used to control the maximum number of concurrent searches allowed in this phase. The default is based on the number of data nodes and the default search thread pool size.

collapse cannot be used in conjunction with scroll, rescore or search after.

Second level of collapsing

Second level of collapsing is also supported and is applied to inner_hits. For example, the following request finds the top scored tweets for each country, and within each country finds the top scored tweets for each user.

Response:

Second level of collapsing doesnb t allow inner_hits.

From / Size

Pagination of results can be done by using the from and size parameters. The from parameter defines the offset from the first result you want to fetch. The size parameter allows you to configure the maximum amount of hits to be returned.

Though from and size can be set as request parameters, they can also be set within the search body. from defaults to 0, and size defaults to 10.

Note that from + size can not be more than the index.max_result_window index setting which defaults to 10,000. See the Scroll or Search After API for more efficient ways to do deep scrolling.

Highlighting

Highlighters enable you to get highlighted snippets from one or more fields in your search results so you can show users where the query matches are. When you request highlights, the response contains an additional highlight element for each search hit that includes the highlighted fields and the highlighted fragments.

Highlighters donb t reflect the boolean logic of a query when extracting terms to highlight. Thus, for some complex boolean queries (e.g nested boolean queries, queries using minimum_should_match etc.), parts of documents may be highlighted that donb t correspond to query matches.

Highlighting requires the actual content of a field. If the field is not stored (the mapping does not set store to true), the actual _source is loaded and the relevant field is extracted from _source.

For example, to get highlights for the content field in each search hit using the default highlighter, include a highlight object in the request body that specifies the content field:

Elasticsearch supports three highlighters: unified, plain, and fvh (fast vector highlighter). You can specify the highlighter type you want to use for each field.

Unified highlighter

The unified highlighter uses the Lucene Unified Highlighter. This highlighter breaks the text into sentences and uses the BM25 algorithm to score individual sentences as if they were documents in the corpus. It also supports accurate phrase and multi-term (fuzzy, prefix, regex) highlighting. This is the default highlighter.

Plain highlighter

The plain highlighter uses the standard Lucene highlighter. It attempts to reflect the query matching logic in terms of understanding word importance and any word positioning criteria in phrase queries.

The plain highlighter works best for highlighting simple query matches in a single field. To accurately reflect query logic, it creates a tiny in-memory index and re-runs the original query criteria through Luceneb s query execution planner to get access to low-level match information for the current document. This is repeated for every field and every document that needs to be highlighted. If you want to highlight a lot of fields in a lot of documents with complex queries, we recommend using the unified highlighter on postings or term_vector fields.

Fast vector highlighter

The fvh highlighter uses the Lucene Fast Vector highlighter. This highlighter can be used on fields with term_vector set to with_positions_offsets in the mapping. The fast vector highlighter:

 Can be customized with a boundary_scanner. 

 Requires setting term_vector to with_positions_offsets which increases the size of the index 

 Can combine matches from multiple fields into one result. See matched_fields 

 Can assign different weights to matches at different positions allowing for things like phrase matches being sorted above term matches when highlighting a Boosting Query that boosts phrase matches over term matches 

The fvh highlighter does not support span queries. If you need support for span queries, try an alternative highlighter, such as the unified highlighter.

Offsets Strategy

To create meaningful search snippets from the terms being queried, the highlighter needs to know the start and end character offsets of each word in the original text. These offsets can be obtained from:

 The postings list. If index_options is set to offsets in the mapping, the unified highlighter uses this information to highlight documents without re-analyzing the text. It re-runs the original query directly on the postings and extracts the matching offsets from the index, limiting the collection to the highlighted documents. This is important if you have large fields because it doesnb t require reanalyzing the text to be highlighted. It also requires less disk space than using term_vectors. 

 Term vectors. If term_vector information is provided by setting term_vector to with_positions_offsets in the mapping, the unified highlighter automatically uses the term_vector to highlight the field. Itb s fast especially for large fields (> 1MB) and for highlighting multi-term queries like prefix or wildcard because it can access the dictionary of terms for each document. The fvh highlighter always uses term vectors. 

 Plain highlighting. This mode is used by the unified when there is no other alternative. It creates a tiny in-memory index and re-runs the original query criteria through Luceneb s query execution planner to get access to low-level match information on the current document. This is repeated for every field and every document that needs highlighting. The plain highlighter always uses plain highlighting. 

Plain highlighting for large texts may require substantial amount of time and memory. To protect against this, the maximum number of text characters that will be analyzed has been limited to 1000000. This default limit can be changed for a particular index with the index setting index.highlight.max_analyzed_offset.

Highlighting Settings

Highlighting settings can be set on a global level and overridden at the field level.

 boundary_chars  A string that contains each boundary character. Defaults to .,!? \t\n.  boundary_max_scan  How far to scan for boundary characters. Defaults to 20.  boundary_scanner  Specifies how to break the highlighted fragments: chars, sentence, or word. Only valid for the unified and fvh highlighters. Defaults to sentence for the unified highlighter. Defaults to chars for the fvh highlighter. 

 chars  Use the characters specified by boundary_chars as highlighting boundaries. The boundary_max_scan setting controls how far to scan for boundary characters. Only valid for the fvh highlighter.  sentence  Break highlighted fragments at the next sentence boundary, as determined by Javab s BreakIterator. You can specify the locale to use with boundary_scanner_locale. 

When used with the unified highlighter, the sentence scanner splits sentences bigger than fragment_size at the first word boundary next to fragment_size. You can set fragment_size to 0 to never split any sentence.

 word  Break highlighted fragments at the next word boundary, as determined by Javab s BreakIterator. You can specify the locale to use with boundary_scanner_locale.  boundary_scanner_locale  Controls which locale is used to search for sentence and word boundaries. This parameter takes a form of a language tag, e.g. "en-US", "fr-FR", "ja-JP". More info can be found in the Locale Language Tag documentation. The default value is  Locale.ROOT.  encoder  Indicates if the snippet should be HTML encoded: default (no encoding) or html (HTML-escape the snippet text and then insert the highlighting tags)  fields  Specifies the fields to retrieve highlights for. You can use wildcards to specify fields. For example, you could specify comment_* to get highlights for all text and keyword fields that start with comment_. 

Only text and keyword fields are highlighted when you use wildcards. If you use a custom mapper and want to highlight on a field anyway, you must explicitly specify that field name.

 force_source  Highlight based on the source even if the field is stored separately. Defaults to false.  fragmenter  Specifies how text should be broken up in highlight snippets: simple or span. Only valid for the plain highlighter. Defaults to span. 

 simple  Breaks up text into same-sized fragments.  span  Breaks up text into same-sized fragments, but tried to avoid breaking up text between highlighted terms. This is helpful when youb re querying for phrases. Default.  fragment_offset  Controls the margin from which you want to start highlighting. Only valid when using the fvh highlighter.  fragment_size  The size of the highlighted fragment in characters. Defaults to 100.  highlight_query  Highlight matches for a query other than the search query. This is especially useful if you use a rescore query because those are not taken into account by highlighting by default. 

Elasticsearch does not validate that highlight_query contains the search query in any way so it is possible to define it so legitimate query results are not highlighted. Generally, you should include the search query as part of the highlight_query.

 matched_fields  Combine matches on multiple fields to highlight a single field. This is most intuitive for multifields that analyze the same string in different ways. All matched_fields must have term_vector set to with_positions_offsets, but only the field to which the matches are combined is loaded so only that field benefits from having store set to yes. Only valid for the fvh highlighter.  no_match_size  The amount of text you want to return from the beginning of the field if there are no matching fragments to highlight. Defaults to 0 (nothing is returned).  number_of_fragments  The maximum number of fragments to return. If the number of fragments is set to 0, no fragments are returned. Instead, the entire field contents are highlighted and returned. This can be handy when you need to highlight short texts such as a title or address, but fragmentation is not required. If number_of_fragments is 0, fragment_size is ignored. Defaults to 5.  order  Sorts highlighted fragments by score when set to score. By default, fragments will be output in the order they appear in the field (order: none). Setting this option to score will output the most relevant fragments first. Each highlighter applies its own logic to compute relevancy scores. See the document How highlighters work internally for more details how different highlighters find the best fragments.  phrase_limit  Controls the number of matching phrases in a document that are considered. Prevents the fvh highlighter from analyzing too many phrases and consuming too much memory. When using matched_fields, phrase_limit phrases per matched field are considered. Raising the limit increases query time and consumes more memory. Only supported by the fvh highlighter. Defaults to 256.  pre_tags  Use in conjunction with post_tags to define the HTML tags to use for the highlighted text. By default, highlighted text is wrapped in <em> and </em> tags. Specify as an array of strings.  post_tags  Use in conjunction with pre_tags to define the HTML tags to use for the highlighted text. By default, highlighted text is wrapped in <em> and </em> tags. Specify as an array of strings.  require_field_match  By default, only fields that contains a query match are highlighted. Set require_field_match to false to highlight all fields. Defaults to true.  tags_schema  Set to styled to use the built-in tag schema. The styled schema defines the following pre_tags and defines post_tags as </em>. 

 type  The highlighter to use: unified, plain, or fvh. Defaults to unified. Highlighting Examples

 Override global settings 

 Specify a highlight query 

 Set highlighter type 

 Configure highlighting tags 

 Highlight source 

 Highlight all fields 

 Combine matches on multiple fields 

 Explicitly order highlighted fields 

 Control highlighted fragments 

 Highlight using the postings list 

 Specify a fragmenter for the plain highlighter 

Override global settings

You can specify highlighter settings globally and selectively override them for individual fields.

Specify a highlight query

You can specify a highlight_query to take additional information into account when highlighting. For example, the following query includes both the search query and rescore query in the highlight_query. Without the highlight_query, highlighting would only take the search query into account.

Set highlighter type

The type field allows to force a specific highlighter type. The allowed values are: unified, plain and fvh. The following is an example that forces the use of the plain highlighter:

Configure highlighting tags

By default, the highlighting will wrap highlighted text in <em> and </em>. This can be controlled by setting pre_tags and post_tags, for example:

When using the fast vector highlighter, you can specify additional tags and the "importance" is ordered.

You can also use the built-in styled tag schema:

Highlight on source

Forces the highlighting to highlight fields based on the source even if fields are stored separately. Defaults to false.

Highlight in all fields

By default, only fields that contains a query match are highlighted. Set require_field_match to false to highlight all fields.

Combine matches on multiple fields

This is only supported by the fvh highlighter

The Fast Vector Highlighter can combine matches on multiple fields to highlight a single field. This is most intuitive for multifields that analyze the same string in different ways. All matched_fields must have term_vector set to with_positions_offsets but only the field to which the matches are combined is loaded so only that field would benefit from having store set to yes.

In the following examples, comment is analyzed by the english analyzer and comment.plain is analyzed by the standard analyzer.

The above matches both "run with scissors" and "running with scissors" and would highlight "running" and "scissors" but not "run". If both phrases appear in a large document then "running with scissors" is sorted above "run with scissors" in the fragments list because there are more matches in that fragment.

The above highlights "run" as well as "running" and "scissors" but still sorts "running with scissors" above "run with scissors" because the plain match ("running") is boosted.

The above query wouldnb t highlight "run" or "scissor" but shows that it is just fine not to list the field to which the matches are combined (comment) in the matched fields.

Technically it is also fine to add fields to matched_fields that donb t share the same underlying string as the field to which the matches are combined. The results might not make much sense and if one of the matches is off the end of the text then the whole query will fail.

There is a small amount of overhead involved with setting matched_fields to a non-empty array so always prefer

to

Explicitly order highlighted fields

Elasticsearch highlights the fields in the order that they are sent, but per the JSON spec, objects are unordered. If you need to be explicit about the order in which fields are highlighted specify the fields as an array:

None of the highlighters built into Elasticsearch care about the order that the fields are highlighted but a plugin might.

Control highlighted fragments

Each field highlighted can control the size of the highlighted fragment in characters (defaults to 100), and the maximum number of fragments to return (defaults to 5). For example:

On top of this it is possible to specify that highlighted fragments need to be sorted by score:

If the number_of_fragments value is set to 0 then no fragments are produced, instead the whole content of the field is returned, and of course it is highlighted. This can be very handy if short texts (like document title or address) need to be highlighted but no fragmentation is required. Note that fragment_size is ignored in this case.

When using fvh one can use fragment_offset parameter to control the margin to start highlighting from.

In the case where there is no matching fragment to highlight, the default is to not return anything. Instead, we can return a snippet of text from the beginning of the field by setting no_match_size (default 0) to the length of the text that you want returned. The actual length may be shorter or longer than specified as it tries to break on a word boundary.

Highlight using the postings list

Here is an example of setting the comment field in the index mapping to allow for highlighting using the postings:

Here is an example of setting the comment field to allow for highlighting using the term_vectors (this will cause the index to be bigger):

Specify a fragmenter for the plain highlighter

When using the plain highlighter, you can choose between the simple and span fragmenters:

Response:

Response:

If the number_of_fragments option is set to 0, NullFragmenter is used which does not fragment the text at all. This is useful for highlighting the entire contents of a document or field.

How highlighters work internally

Given a query and a text (the content of a document field), the goal of a highlighter is to find the best text fragments for the query, and highlight the query terms in the found fragments. For this, a highlighter needs to address several questions:

 How break a text into fragments? 

 How to find the best fragments among all fragments? 

 How to highlight the query terms in a fragment? 

How to break a text into fragments?

Relevant settings: fragment_size, fragmenter, type of highlighter, boundary_chars, boundary_max_scan, boundary_scanner, boundary_scanner_locale.

Plain highlighter begins with analyzing the text using the given analyzer, and creating a token stream from it. Plain highlighter uses a very simple algorithm to break the token stream into fragments. It loops through terms in the token stream, and every time the current termb s end_offset exceeds fragment_size multiplied by the number of created fragments, a new fragment is created. A little more computation is done with using span fragmenter to avoid breaking up text between highlighted terms. But overall, since the breaking is done only by fragment_size, some fragments can be quite odd, e.g. beginning with a punctuation mark.

Unified or FVH highlighters do a better job of breaking up a text into fragments by utilizing Javab s BreakIterator. This ensures that a fragment is a valid sentence as long as fragment_size allows for this.

How to find the best fragments?

Relevant settings: number_of_fragments.

To find the best, most relevant, fragments, a highlighter needs to score each fragment in respect to the given query. The goal is to score only those terms that participated in generating the hit on the document. For some complex queries, this is still work in progress.

The plain highlighter creates an in-memory index from the current token stream, and re-runs the original query criteria through Luceneb s query execution planner to get access to low-level match information for the current text. For more complex queries the original query could be converted to a span query, as span queries can handle phrases more accurately. Then this obtained low-level match information is used to score each individual fragment. The scoring method of the plain highlighter is quite simple. Each fragment is scored by the number of unique query terms found in this fragment. The score of individual term is equal to its boost, which is by default is 1. Thus, by default, a fragment that contains one unique query term, will get a score of 1; and a fragment that contains two unique query terms, will get a score of 2 and so on. The fragments are then sorted by their scores, so the highest scored fragments will be output first.

FVH doesnb t need to analyze the text and build an in-memory index, as it uses pre-indexed document term vectors, and finds among them terms that correspond to the query. FVH scores each fragment by the number of query terms found in this fragment. Similarly to plain highlighter, score of individual term is equal to its boost value. In contrast to plain highlighter, all query terms are counted, not only unique terms.

Unified highlighter can use pre-indexed term vectors or pre-indexed terms offsets, if they are available. Otherwise, similar to Plain Highlighter, it has to create an in-memory index from the text. Unified highlighter uses the BM25 scoring model to score fragments.

How to highlight the query terms in a fragment?

Relevant settings: pre-tags, post-tags.

The goal is to highlight only those terms that participated in generating the hit on the document. For some complex boolean queries, this is still work in progress, as highlighters donb t reflect the boolean logic of a query and only extract leaf (terms, phrases, prefix etc) queries.

Plain highlighter given the token stream and the original text, recomposes the original text to highlight only terms from the token stream that are contained in the low-level match information structure from the previous step.

FVH and unified highlighter use intermediate data structures to represent fragments in some raw form, and then populate them with actual text.

A highlighter uses pre-tags, post-tags to encode highlighted terms.

An example of the work of the unified highlighter

Letb s look in more details how unified highlighter works.

First, we create a index with a text field content, that will be indexed using english analyzer, and will be indexed without offsets or term vectors.

We put the following document into the index:

And we ran the following query with a highlight request:

After doc1 is found as a hit for this query, this hit will be passed to the unified highlighter for highlighting the field content of the document. Since the field content was not indexed either with offsets or term vectors, its raw field value will be analyzed, and in-memory index will be built from the terms that match the query:

{"token":"onli","start_offset":12,"end_offset":16,"position":3}, {"token":"fox","start_offset":19,"end_offset":22,"position":5}, {"token":"fox","start_offset":53,"end_offset":58,"position":11}, {"token":"onli","start_offset":117,"end_offset":121,"position":24}, {"token":"onli","start_offset":159,"end_offset":163,"position":34}, {"token":"fox","start_offset":164,"end_offset":167,"position":35}Our complex phrase query will be converted to the span query: spanNear([text:onli, text:fox], 0, true), meaning that we are looking for terms "onli: and "fox" within 0 distance from each other, and in the given order. The span query will be run against the created before in-memory index, to find the following match:

{"term":"onli", "start_offset":159, "end_offset":163}, {"term":"fox", "start_offset":164, "end_offset":167}In our example, we have got a single match, but there could be several matches. Given the matches, the unified highlighter breaks the text of the field into so called "passages". Each passage must contain at least one match. The unified highlighter with the use of Javab s BreakIterator ensures that each passage represents a full sentence as long as it doesnb t exceed fragment_size. For our example, we have got a single passage with the following properties (showing only a subset of the properties here):

Passage: startOffset: 147 endOffset: 189 score: 3.7158387 matchStarts: [159, 164] matchEnds: [163, 167] numMatches: 2Notice how a passage has a score, calculated using the BM25 scoring formula adapted for passages. Scores allow us to choose the best scoring passages if there are more passages available than the requested by the user number_of_fragments. Scores also let us to sort passages by order: "score" if requested by the user.

As the final step, the unified highlighter will extract from the fieldb s text a string corresponding to each passage:

"I'll be the only fox in the world for you."and will format with the tags <em> and </em> all matches in this string using the passagesb s matchStarts and matchEnds information:

I'll be the <em>only</em> <em>fox</em> in the world for you.This kind of formatted strings are the final result of the highlighter returned to the user.


Index Boost

Allows to configure different boost level per index when searching across more than one indices. This is very handy when hits coming from one index matter more than hits coming from another index (think social graph where each user has an index).

Deprecated in 5.2.0.  This format is deprecated. Please use array format instead. 

You can also specify it as an array to control the order of boosts.

This is important when you use aliases or wildcard expression. If multiple matches are found, the first match will be used. For example, if an index is included in both alias1 and index*, boost value of 1.4 is applied.

Inner hits

The parent-join and nested features allow the return of documents that have matches in a different scope. In the parent/child case, parent documents are returned based on matches in child documents or child documents are returned based on matches in parent documents. In the nested case, documents are returned based on matches in nested inner objects.

In both cases, the actual matches in the different scopes that caused a document to be returned are hidden. In many cases, itb s very useful to know which inner nested objects (in the case of nested) or children/parent documents (in the case of parent/child) caused certain information to be returned. The inner hits feature can be used for this. This feature returns per search hit in the search response additional nested hits that caused a search hit to match in a different scope.

Inner hits can be used by defining an inner_hits definition on a nested, has_child or has_parent query and filter. The structure looks like this:

If inner_hits is defined on a query that supports it then each search hit will contain an inner_hits json object with the following structure:

Options

Inner hits support the following options:

  from 

   The offset from where the first hit to fetch for each inner_hits in the returned regular search hits. 

   size 

   The maximum number of hits to return per inner_hits. By default the top three matching hits are returned. 

   sort 

   How the inner hits should be sorted per inner_hits. By default the hits are sorted by the score. 

   name 

   The name to be used for the particular inner hit definition in the response. Useful when multiple inner hits have been defined in a single search request. The default depends in which query the inner hit is defined. For has_child query and filter this is the child type, has_parent query and filter this is the parent type and the nested query and filter this is the nested path. 

 Inner hits also supports the following per document features:

 Highlighting 

 Explain 

 Source filtering 

 Script fields 

 Doc value fields 

 Include versions 

 Include Sequence Numbers and Primary Terms 

Nested inner hits

The nested inner_hits can be used to include nested inner objects as inner hits to a search hit.

 

 The inner hit definition in the nested query. No other options need to be defined. 

An example of a response snippet that could be generated from the above search request:

 

 The name used in the inner hit definition in the search request. A custom key can be used via the name option. 

The _nested metadata is crucial in the above example, because it defines from what inner nested object this inner hit came from. The field defines the object array field the nested hit is from and the offset relative to its location in the _source. Due to sorting and scoring the actual location of the hit objects in the inner_hits is usually different than the location a nested inner object was defined.

By default the _source is returned also for the hit objects in inner_hits, but this can be changed. Either via _source filtering feature part of the source can be returned or be disabled. If stored fields are defined on the nested level these can also be returned via the fields feature.

An important default is that the _source returned in hits inside inner_hits is relative to the _nested metadata. So in the above example only the comment part is returned per nested hit and not the entire source of the top level document that contained the comment.

Nested inner hits and _source

Nested document donb t have a b _source` field, because the entire source of document is stored with the root document under its _source field. To include the source of just the nested document, the source of the root document is parsed and just the relevant bit for the nested document is included as source in the inner hit. Doing this for each matching nested document has an impact on the time it takes to execute the entire search request, especially when size and the inner hitsb  size are set higher than the default. To avoid the relatively expensive source extraction for nested inner hits, one can disable including the source and solely rely on doc values fields. Like this:

Hierarchical levels of nested object fields and inner hits.

If a mapping has multiple levels of hierarchical nested object fields each level can be accessed via dot notated path. For example if there is a comments nested field that contains a votes nested field and votes should directly be returned with the root hits then the following path can be defined:

Which would look like:

This indirect referencing is only supported for nested inner hits.

Parent/child inner hits

The parent/child inner_hits can be used to include parent or child:

  

 The inner hit definition like in the nested example. 

An example of a response snippet that could be generated from the above search request:

min_score

Exclude documents which have a _score less than the minimum specified in min_score:

Note, most times, this does not make much sense, but is provided for advanced use cases.

Named Queries

Each filter and query can accept a _name in its top level definition.

The search response will include for each hit the matched_queries it matched on. The tagging of queries and filters only make sense for the bool query.

Post filter

The post_filter is applied to the search hits at the very end of a search request, after aggregations have already been calculated. Its purpose is best explained by example:

Imagine that you are selling shirts that have the following properties:

Imagine a user has specified two filters:

color:red and brand:gucci. You only want to show them red shirts made by Gucci in the search results. Normally you would do this with a bool query:

However, you would also like to use faceted navigation to display a list of other options that the user could click on. Perhaps you have a model field that would allow the user to limit their search results to red Gucci t-shirts or dress-shirts.

This can be done with a terms aggregation:

 

 Returns the most popular models of red shirts by Gucci. 

But perhaps you would also like to tell the user how many Gucci shirts are available in other colors. If you just add a terms aggregation on the color field, you will only get back the color red, because your query returns only red shirts by Gucci.

Instead, you want to include shirts of all colors during aggregation, then apply the colors filter only to the search results. This is the purpose of the post_filter:

 

 The main query now finds all shirts by Gucci, regardless of color. 

 

 The colors agg returns popular colors for shirts by Gucci. 

  

 The color_red agg limits the models sub-aggregation to red Gucci shirts. 

 

 Finally, the post_filter removes colors other than red from the search hits. 

Preference

Controls a preference of the shard copies on which to execute the search. By default, Elasticsearch selects from the available shard copies in an unspecified order, taking the allocation awareness and adaptive replica selection configuration into account. However, it may sometimes be desirable to try and route certain searches to certain sets of shard copies, for instance to make better use of per-copy caches.

The preference is a query string parameter which can be set to:

  _only_local 

   The operation will be executed only on shards allocated to the local node. 

   _local 

   The operation will be executed on shards allocated to the local node if possible, and will fall back to other shards if not. 

   _prefer_nodes:abc,xyz 

   The operation will be executed on nodes with one of the provided node ids (abc or xyz in this case) if possible. If suitable shard copies exist on more than one of the selected nodes then the order of preference between these copies is unspecified. 

   _shards:2,3 

   Restricts the operation to the specified shards. (2 and 3 in this case). This preference can be combined with other preferences but it has to appear first: _shards:2,3|_local 

   _only_nodes:abc*,x*yz,... 

   Restricts the operation to nodes specified according to the node specification. If suitable shard copies exist on more than one of the selected nodes then the order of preference between these copies is unspecified. 

   Custom (string) value 

   Any value that does not start with _. If two searches both give the same custom string value for their preference and the underlying cluster state does not change then the same ordering of shards will be used for the searches. This does not guarantee that the exact same shards will be used each time: the cluster state, and therefore the selected shards, may change for a number of reasons including shard relocations and shard failures, and nodes may sometimes reject searches causing fallbacks to alternative nodes. However, in practice the ordering of shards tends to remain stable for long periods of time. A good candidate for a custom preference value is something like the web session id or the user name. 

 For instance, use the userb s session ID xyzabc123 as follows:

The _only_local preference guarantees only to use shard copies on the local node, which is sometimes useful for troubleshooting. All other options do not fully guarantee that any particular shard copies are used in a search, and on a changing index this may mean that repeated searches may yield different results if they are executed on different shard copies which are in different refresh states.

Query

The query element within the search request body allows to define a query using the Query DSL.

Rescoring

Rescoring can help to improve precision by reordering just the top (eg 100 - 500) documents returned by the query and post_filter phases, using a secondary (usually more costly) algorithm, instead of applying the costly algorithm to all documents in the index.

A rescore request is executed on each shard before it returns its results to be sorted by the node handling the overall search request.

Currently the rescore API has only one implementation: the query rescorer, which uses a query to tweak the scoring. In the future, alternative rescorers may be made available, for example, a pair-wise rescorer.

An error will be thrown if an explicit sort (other than _score in descending order) is provided with a rescore query.

when exposing pagination to your users, you should not change window_size as you step through each page (by passing different from values) since that can alter the top hits causing results to confusingly shift as the user steps through pages.

Query rescorer

The query rescorer executes a second query only on the Top-K results returned by the query and post_filter phases. The number of docs which will be examined on each shard can be controlled by the window_size parameter, which defaults to 10.

By default the scores from the original query and the rescore query are combined linearly to produce the final _score for each document. The relative importance of the original query and of the rescore query can be controlled with the query_weight and rescore_query_weight respectively. Both default to 1.

For example:

The way the scores are combined can be controlled with the score_mode:

Score Mode Descriptiontotal

Add the original score and the rescore query score. The default.

multiply

Multiply the original score by the rescore query score. Useful for function query rescores.

avg

Average the original score and the rescore query score.

max

Take the max of original score and the rescore query score.

min

Take the min of the original score and the rescore query score.

Multiple Rescores

It is also possible to execute multiple rescores in sequence:

The first one gets the results of the query then the second one gets the results of the first, etc. The second rescore will "see" the sorting done by the first rescore so it is possible to use a large window on the first rescore to pull documents into a smaller window for the second rescore.

Script Fields

Allows to return a script evaluation (based on different fields) for each hit, for example:

Script fields can work on fields that are not stored (my_field_name in the above case), and allow to return custom values to be returned (the evaluated value of the script).

Script fields can also access the actual _source document and extract specific elements to be returned from it by using params['_source']. Here is an example:

Note the _source keyword here to navigate the json-like model.

Itb s important to understand the difference between doc['my_field'].value and params['_source']['my_field']. The first, using the doc keyword, will cause the terms for that field to be loaded to memory (cached), which will result in faster execution, but more memory consumption. Also, the doc[...] notation only allows for simple valued fields (you canb t return a json object from it) and makes sense only for non-analyzed or single term based fields. However, using doc is still the recommended way to access values from the document, if at all possible, because _source must be loaded and parsed every time itb s used. Using _source is very slow.

Scroll

While a search request returns a single b pageb  of results, the scroll API can be used to retrieve large numbers of results (or even all results) from a single search request, in much the same way as you would use a cursor on a traditional database.

Scrolling is not intended for real time user requests, but rather for processing large amounts of data, e.g. in order to reindex the contents of one index into a new index with a different configuration.

Client support for scrolling and reindexing

Some of the officially supported clients provide helpers to assist with scrolled searches and reindexing of documents from one index to another:

 Perl  See Search::Elasticsearch::Client::5_0::Bulk and Search::Elasticsearch::Client::5_0::Scroll  Python  See elasticsearch.helpers.* The results that are returned from a scroll request reflect the state of the index at the time that the initial search request was made, like a snapshot in time. Subsequent changes to documents (index, update or delete) will only affect later search requests.

In order to use scrolling, the initial search request should specify the scroll parameter in the query string, which tells Elasticsearch how long it should keep the b search contextb  alive (see Keeping the search context alive), eg ?scroll=1m.

The result from the above request includes a _scroll_id, which should be passed to the scroll API in order to retrieve the next batch of results.

 

 GET or POST can be used and the URL should not include the index name b  this is specified in the original search request instead. 

 

 The scroll parameter tells Elasticsearch to keep the search context open for another 1m. 

 

 The scroll_id parameter 

The size parameter allows you to configure the maximum number of hits to be returned with each batch of results. Each call to the scroll API returns the next batch of results until there are no more results left to return, ie the hits array is empty.

The initial search request and each subsequent scroll request each return a _scroll_id. While the _scroll_id may change between requests, it doesnb t always change b  in any case, only the most recently received _scroll_id should be used.

If the request specifies aggregations, only the initial search response will contain the aggregations results.

Scroll requests have optimizations that make them faster when the sort order is _doc. If you want to iterate over all documents regardless of the order, this is the most efficient option:

Keeping the search context alive

The scroll parameter (passed to the search request and to every scroll request) tells Elasticsearch how long it should keep the search context alive. Its value (e.g. 1m, see Time units

) does not need to be long enough to process all data b  it just needs to be long enough to process the previous batch of results. Each scroll request (with the scroll parameter) sets a new expiry time. If a scroll request doesnb t pass in the scroll parameter, then the search context will be freed as part of that scroll request.

Normally, the background merge process optimizes the index by merging together smaller segments to create new bigger segments, at which time the smaller segments are deleted. This process continues during scrolling, but an open search context prevents the old segments from being deleted while they are still in use. This is how Elasticsearch is able to return the results of the initial search request, regardless of subsequent changes to documents.

Keeping older segments alive means that more file handles are needed. Ensure that you have configured your nodes to have ample free file handles. See File Descriptors.

To prevent against issues caused by having too many scrolls open, the user is not allowed to open scrolls past a certain limit. By default, the maximum number of open scrolls is 500. This limit can be updated with the search.max_open_scroll_context cluster setting.

You can check how many search contexts are open with the nodes stats API:

Clear scroll API

Search context are automatically removed when the scroll timeout has been exceeded. However keeping scrolls open has a cost, as discussed in the previous section so scrolls should be explicitly cleared as soon as the scroll is not being used anymore using the clear-scroll API:

Multiple scroll IDs can be passed as array:

All search contexts can be cleared with the _all parameter:

The scroll_id can also be passed as a query string parameter or in the request body. Multiple scroll IDs can be passed as comma separated values:

Sliced Scroll

For scroll queries that return a lot of documents it is possible to split the scroll in multiple slices which can be consumed independently:

 

 The id of the slice 

 

 The maximum number of slices 

The result from the first request returned documents that belong to the first slice (id: 0) and the result from the second request returned documents that belong to the second slice. Since the maximum number of slices is set to 2 the union of the results of the two requests is equivalent to the results of a scroll query without slicing. By default the splitting is done on the shards first and then locally on each shard using the _id field with the following formula: slice(doc) = floorMod(hashCode(doc._id), max) For instance if the number of shards is equal to 2 and the user requested 4 slices then the slices 0 and 2 are assigned to the first shard and the slices 1 and 3 are assigned to the second shard.

Each scroll is independent and can be processed in parallel like any scroll request.

If the number of slices is bigger than the number of shards the slice filter is very slow on the first calls, it has a complexity of O(N) and a memory cost equals to N bits per slice where N is the total number of documents in the shard. After few calls the filter should be cached and subsequent calls should be faster but you should limit the number of sliced query you perform in parallel to avoid the memory explosion.

To avoid this cost entirely it is possible to use the doc_values of another field to do the slicing but the user must ensure that the field has the following properties:

 The field is numeric. 

 doc_values are enabled on that field 

 Every document should contain a single value. If a document has multiple values for the specified field, the first value is used. 

 The value for each document should be set once when the document is created and never updated. This ensures that each slice gets deterministic results. 

 The cardinality of the field should be high. This ensures that each slice gets approximately the same amount of documents. 

For append only time-based indices, the timestamp field can be used safely.

By default the maximum number of slices allowed per scroll is limited to 1024. You can update the index.max_slices_per_scroll index setting to bypass this limit.

Search After

Pagination of results can be done by using the from and size but the cost becomes prohibitive when the deep pagination is reached. The index.max_result_window which defaults to 10,000 is a safeguard, search requests take heap memory and time proportional to from + size. The Scroll api is recommended for efficient deep scrolling but scroll contexts are costly and it is not recommended to use it for real time user requests. The search_after parameter circumvents this problem by providing a live cursor. The idea is to use the results from the previous page to help the retrieval of the next page.

Suppose that the query to retrieve the first page looks like this:

 

 A copy of the _id field with doc_values enabled 

A field with one unique value per document should be used as the tiebreaker of the sort specification. Otherwise the sort order for documents that have the same sort values would be undefined and could lead to missing or duplicate results. The _id field has a unique value per document but it is not recommended to use it as a tiebreaker directly. Beware that search_after looks for the first document which fully or partially matches tiebreakerb s provided value. Therefore if a document has a tiebreaker value of "654323" and you search_after for "654" it would still match that document and return results found after it. doc value are disabled on this field so sorting on it requires to load a lot of data in memory. Instead it is advised to duplicate (client side or with a set ingest processor) the content of the _id field in another field that has doc value enabled and to use this new field as the tiebreaker for the sort.

The result from the above request includes an array of sort values for each document. These sort values can be used in conjunction with the search_after parameter to start returning results "after" any document in the result list. For instance we can use the sort values of the last document and pass it to search_after to retrieve the next page of results:

The parameter from must be set to 0 (or -1) when search_after is used.

search_after is not a solution to jump freely to a random page but rather to scroll many queries in parallel. It is very similar to the scroll API but unlike it, the search_after parameter is stateless, it is always resolved against the latest version of the searcher. For this reason the sort order may change during a walk depending on the updates and deletes of your index.

Search Type

There are different execution paths that can be done when executing a distributed search. The distributed search operation needs to be scattered to all the relevant shards and then all the results are gathered back. When doing scatter/gather type execution, there are several ways to do that, specifically with search engines.

One of the questions when executing a distributed search is how many results to retrieve from each shard. For example, if we have 10 shards, the 1st shard might hold the most relevant results from 0 till 10, with other shards results ranking below it. For this reason, when executing a request, we will need to get results from 0 till 10 from all shards, sort them, and then return the results if we want to ensure correct results.

Another question, which relates to the search engine, is the fact that each shard stands on its own. When a query is executed on a specific shard, it does not take into account term frequencies and other search engine information from the other shards. If we want to support accurate ranking, we would need to first gather the term frequencies from all shards to calculate global term frequencies, then execute the query on each shard using these global frequencies.

Also, because of the need to sort the results, getting back a large document set, or even scrolling it, while maintaining the correct sorting behavior can be a very expensive operation. For large result set scrolling, it is best to sort by _doc if the order in which documents are returned is not important.

Elasticsearch is very flexible and allows to control the type of search to execute on a per search request basis. The type can be configured by setting the search_type parameter in the query string. The types are:

Query Then Fetch

Parameter value: query_then_fetch.

The request is processed in two phases. In the first phase, the query is forwarded to all involved shards. Each shard executes the search and generates a sorted list of results, local to that shard. Each shard returns just enough information to the coordinating node to allow it merge and re-sort the shard level results into a globally sorted set of results, of maximum length size.

During the second phase, the coordinating node requests the document content (and highlighted snippets, if any) from only the relevant shards.

This is the default setting, if you do not specify a search_type in your request.

Dfs, Query Then Fetch

Parameter value: dfs_query_then_fetch.

Same as "Query Then Fetch", except for an initial scatter phase which goes and computes the distributed term frequencies for more accurate scoring.

Sequence Numbers and Primary Term

Returns the sequence number and primary term of the last modification to each search hit. See Optimistic concurrency control for more details.

Sort

Allows you to add one or more sorts on specific fields. Each sort can be reversed as well. The sort is defined on a per field level, with special field name for _score to sort by score, and _doc to sort by index order.

Assuming the following index mapping:

_doc has no real use-case besides being the most efficient sort order. So if you donb t care about the order in which documents are returned, then you should sort by _doc. This especially helps when scrolling.

Sort Values

The sort values for each document returned are also returned as part of the response.

Sort Order

The order option can have the following values:

  asc 

   Sort in ascending order 

   desc 

   Sort in descending order 

 The order defaults to desc when sorting on the _score, and defaults to asc when sorting on anything else.

Sort mode option

Elasticsearch supports sorting by array or multi-valued fields. The mode option controls what array value is picked for sorting the document it belongs to. The mode option can have the following values:

  min 

   Pick the lowest value. 

   max 

   Pick the highest value. 

   sum 

   Use the sum of all values as sort value. Only applicable for number based array fields. 

   avg 

   Use the average of all values as sort value. Only applicable for number based array fields. 

   median 

   Use the median of all values as sort value. Only applicable for number based array fields. 

 The default sort mode in the ascending sort order is min b  the lowest value is picked. The default sort mode in the descending order is max b  the highest value is picked.

Sort mode example usage

In the example below the field price has multiple prices per document. In this case the result hits will be sorted by price ascending based on the average price per document.

Sorting within nested objects.

Elasticsearch also supports sorting by fields that are inside one or more nested objects. The sorting by nested field support has a nested sort option with the following properties:

 path  Defines on which nested object to sort. The actual sort field must be a direct field inside this nested object. When sorting by nested field, this field is mandatory.  filter  A filter that the inner objects inside the nested path should match with in order for its field values to be taken into account by sorting. Common case is to repeat the query / filter inside the nested filter or query. By default no nested_filter is active.  max_children  The maximum number of children to consider per root document when picking the sort value. Defaults to unlimited.  nested  Same as top-level nested but applies to another nested path within the current nested object. Nested sort options before Elasticsearch 6.1The nested_path and nested_filter options have been deprecated in favor of the options documented above.

Nested sorting examples

In the below example offer is a field of type nested. The nested path needs to be specified; otherwise, Elasticsearch doesnb t know on what nested level sort values need to be captured.

In the below example parent and child fields are of type nested. The nested_path needs to be specified at each level; otherwise, Elasticsearch doesnb t know on what nested level sort values need to be captured.

Nested sorting is also supported when sorting by scripts and sorting by geo distance.

Missing Values

The missing parameter specifies how docs which are missing the sort field should be treated: The missing value can be set to _last, _first, or a custom value (that will be used for missing docs as the sort value). The default is _last.

For example:

If a nested inner object doesnb t match with the nested_filter then a missing value is used.

Ignoring Unmapped Fields

By default, the search request will fail if there is no mapping associated with a field. The unmapped_type option allows you to ignore fields that have no mapping and not sort by them. The value of this parameter is used to determine what sort values to emit. Here is an example of how it can be used:

If any of the indices that are queried doesnb t have a mapping for price then Elasticsearch will handle it as if there was a mapping of type long, with all documents in this index having no value for this field.

Geo Distance Sorting

Allow to sort by _geo_distance. Here is an example, assuming pin.location is a field of type geo_point:

 distance_type  How to compute the distance. Can either be arc (default), or plane (faster, but inaccurate on long distances and close to the poles).  mode  What to do in case a field has several geo points. By default, the shortest distance is taken into account when sorting in ascending order and the longest distance when sorting in descending order. Supported values are min, max, median and avg.  unit  The unit to use when computing sort values. The default is m (meters).  ignore_unmapped  Indicates if the unmapped field should be treated as a missing value. Setting it to true is equivalent to specifying an unmapped_type in the field sort. The default is false (unmapped field cause the search to fail). geo distance sorting does not support configurable missing values: the distance will always be considered equal to Infinity when a document does not have values for the field that is used for distance computation.

The following formats are supported in providing the coordinates:

Lat Lon as Properties

Lat Lon as String

Format in lat,lon.

Geohash

Lat Lon as Array

Format in [lon, lat], note, the order of lon/lat here in order to conform with GeoJSON.

Multiple reference points

Multiple geo points can be passed as an array containing any geo_point format, for example

and so forth.

The final distance for a document will then be min/max/avg (defined via mode) distance of all points contained in the document to all points given in the sort request.

Script Based Sorting

Allow to sort based on custom scripts, here is an example:

Track Scores

When sorting on a field, scores are not computed. By setting track_scores to true, scores will still be computed and tracked.

Memory Considerations

When sorting, the relevant sorted field values are loaded into memory. This means that per shard, there should be enough memory to contain them. For string based types, the field sorted on should not be analyzed / tokenized. For numeric types, if possible, it is recommended to explicitly set the type to narrower types (like short, integer and float).

Source filtering

Allows to control how the _source field is returned with every hit.

By default operations return the contents of the _source field unless you have used the stored_fields parameter or if the _source field is disabled.

You can turn off _source retrieval by using the _source parameter:

To disable _source retrieval set to false:

The _source also accepts one or more wildcard patterns to control what parts of the _source should be returned:

For example:

Or

Finally, for complete control, you can specify both includes and excludes patterns:

Stored Fields

The stored_fields parameter is about fields that are explicitly marked as stored in the mapping, which is off by default and generally not recommended. Use source filtering instead to select subsets of the original source document to be returned.

Allows to selectively load specific stored fields for each document represented by a search hit.

* can be used to load all stored fields from the document.

An empty array will cause only the _id and _type for each hit to be returned, for example:

If the requested fields are not stored (store mapping set to false), they will be ignored.

Stored field values fetched from the document itself are always returned as an array. On the contrary, metadata fields like _routing are never returned as an array.

Also only leaf fields can be returned via the field option. So object fields canb t be returned and such requests will fail.

Script fields can also be automatically detected and used as fields, so things like _source.obj1.field1 can be used, though not recommended, as obj1.field1 will work as well.

Disable stored fields entirely

To disable the stored fields (and metadata fields) entirely use: _none_:

_source and version parameters cannot be activated if _none_ is used.

Track total hits

Generally the total hit count canb t be computed accurately without visiting all matches, which is costly for queries that match lots of documents. The track_total_hits parameter allows you to control how the total number of hits should be tracked. Given that it is often enough to have a lower bound of the number of hits, such as "there are at least 10000 hits", the default is set to 10,000. This means that requests will count the total hit accurately up to 10,000 hits. Itb s is a good trade off to speed up searches if you donb t need the accurate number of hits after a certain threshold.

When set to true the search response will always track the number of hits that match the query accurately (e.g. total.relation will always be equal to "eq" when track_total_hits is set to true). Otherwise the "total.relation" returned in the "total" object in the search response determines how the "total.value" should be interpreted. A value of "gte" means that the "total.value" is a lower bound of the total hits that match the query and a value of "eq" indicates that "total.value" is the accurate count.

... returns:

 

 The total number of hits that match the query. 

 

 The count is accurate (e.g. "eq" means equals). 

It is also possible to set track_total_hits to an integer. For instance the following query will accurately track the total hit count that match the query up to 100 documents:

The hits.total.relation in the response will indicate if the value returned in hits.total.value is accurate ("eq") or a lower bound of the total ("gte").

For instance the following response:

 

 42 documents match the query 

 

 and the count is accurate ("eq") 

... indicates that the number of hits returned in the total is accurate.

If the total number of his that match the query is greater than the value set in track_total_hits, the total hits in the response will indicate that the returned value is a lower bound:

 

 There are at least 100 documents that match the query 

 

 This is a lower bound ("gte"). 

If you donb t need to track the total number of hits at all you can improve query times by setting this option to false:

... returns:

 

 The total number of hits is unknown. 

Finally you can force an accurate count by setting "track_total_hits" to true in the request.

Version

Returns a version for each search hit.

Search Template

The /_search/template endpoint allows to use the mustache language to pre render search requests, before they are executed and fill existing templates with template parameters.

For more information on how Mustache templating and what kind of templating you can do with it check out the online documentation of the mustache project.

The mustache language is implemented in Elasticsearch as a sandboxed scripting language, hence it obeys settings that may be used to enable or disable scripts per type and context as described in the scripting docs

More template examples

Filling in a query string with a single value

Converting parameters to JSON

The {{#toJson}}parameter{{/toJson}} function can be used to convert parameters like maps and array to their JSON representation:

which is rendered as:

A more complex example substitutes an array of JSON objects:

which is rendered as:

Concatenating array of values

The {{#join}}array{{/join}} function can be used to concatenate the values of an array as a comma delimited string:

which is rendered as:

The function also accepts a custom delimiter:

which is rendered as:

Default values

A default value is written as {{var}}{{^var}}default{{/var}} for instance:

When params is { "start": 10, "end": 15 } this query would be rendered as:

But when params is { "start": 10 } this query would use the default value for end:

Conditional clauses

Conditional clauses cannot be expressed using the JSON form of the template. Instead, the template must be passed as a string. For instance, letb s say we wanted to run a match query on the line field, and optionally wanted to filter by line numbers, where start and end are optional.

The params would look like:

   

 All three of these elements are optional. 

We could write the query as:

 

 Fill in the value of param text 

  

 Include the range filter only if line_no is specified 

  

 Include the gte clause only if line_no.start is specified 

 

 Fill in the value of param line_no.start 

 

 Add a comma after the gte clause only if line_no.start AND line_no.end are specified 

  

 Include the lte clause only if line_no.end is specified 

 

 Fill in the value of param line_no.end 

As written above, this template is not valid JSON because it includes the section markers like {{#line_no}}. For this reason, the template should either be stored in a file (see Pre-registered template

) or, when used via the REST API, should be written as a string:

Encoding URLs

The {{#url}}value{{/url}} function can be used to encode a string value in a HTML encoding form as defined in by the HTML specification.

As an example, it is useful to encode a URL:

The previous query will be rendered as:

Pre-registered template

You can register search templates by using the stored scripts api.

This template can be retrieved by

which is rendered as:

This template can be deleted by

To use a stored template at search time use:

 

 Name of the stored template script. 

Validating templates

A template can be rendered in a response with given parameters using

This call will return the rendered template:

 

 status array has been populated with values from the params object. 

Pre-registered templates can also be rendered using

Explain

You can use explain parameter when running a template:

Profiling

You can use profile parameter when running a template:

Multi Search Template

The multi search template API allows to execute several search template requests within the same API using the _msearch/template endpoint.

The format of the request is similar to the Multi Search API format:

The header part supports the same index, search_type, preference, and routing options as the usual Multi Search API.

The body includes a search template body request and supports inline, stored and file templates. Here is an example:

 

 Inline search template request 

 

 Search template request based on a stored template 

The response returns a responses array, which includes the search template response for each search template request matching its order in the original multi search template request. If there was a complete failure for that specific search template request, an object with error message will be returned in place of the actual search response.

Search Shards API

The search shards api returns the indices and shards that a search request would be executed against. This can give useful feedback for working out issues or planning optimizations with routing and shard preferences. When filtered aliases are used, the filter is returned as part of the indices section [5.1.0] Added in 5.1.0.

The index may be a single value, or comma-separated.

Usage

Full example:

This will yield the following result:

And specifying the same request, this time with a routing value:

This will yield the following result:

This time the search will only be executed against two of the shards, because routing values have been specified.

All parameters:

  routing 

   A comma-separated list of routing values to take into account when determining which shards a request would be executed against. 

   preference 

   Controls a preference of which shard replicas to execute the search request on. By default, the operation is randomized between the shard replicas. See the preference documentation for a list of all acceptable values. 

   local 

   A boolean value whether to read the cluster state locally in order to determine where shards are allocated instead of using the Master nodeb s cluster state. 

 Suggesters

The suggest feature suggests similar looking terms based on a provided text by using a suggester. Parts of the suggest feature are still under development.

The suggest request part is defined alongside the query part in a _search request. If the query part is left out, only suggestions are returned.

_suggest endpoint has been deprecated in favour of using suggest via _search endpoint. In 5.0, the _search endpoint has been optimized for suggest only search requests.

Several suggestions can be specified per request. Each suggestion is identified with an arbitrary name. In the example below two suggestions are requested. Both my-suggest-1 and my-suggest-2 suggestions use the term suggester, but have a different text.

The below suggest response example includes the suggestion response for my-suggest-1 and my-suggest-2. Each suggestion part contains entries. Each entry is effectively a token from the suggest text and contains the suggestion entry text, the original start offset and length in the suggest text and if found an arbitrary number of options.

Each options array contains an option object that includes the suggested text, its document frequency and score compared to the suggest entry text. The meaning of the score depends on the used suggester. The term suggesterb s score is based on the edit distance.

Global suggest text

To avoid repetition of the suggest text, it is possible to define a global text. In the example below the suggest text is defined globally and applies to the my-suggest-1 and my-suggest-2 suggestions.

The suggest text can in the above example also be specified as suggestion specific option. The suggest text specified on suggestion level override the suggest text on the global level.

Term suggester

In order to understand the format of suggestions, please read the Suggesters page first.

The term suggester suggests terms based on edit distance. The provided suggest text is analyzed before terms are suggested. The suggested terms are provided per analyzed suggest text token. The term suggester doesnb t take the query into account that is part of request.

Common suggest options:

  text 

   The suggest text. The suggest text is a required option that needs to be set globally or per suggestion. 

   field 

   The field to fetch the candidate suggestions from. This is an required option that either needs to be set globally or per suggestion. 

   analyzer 

   The analyzer to analyse the suggest text with. Defaults to the search analyzer of the suggest field. 

   size 

   The maximum corrections to be returned per suggest text token. 

   sort 

   Defines how suggestions should be sorted per suggest text term. Two possible values: 

  score: Sort by score first, then document frequency and then the term itself. 

 frequency: Sort by document frequency first, then similarity score and then the term itself. 

   suggest_mode 

   The suggest mode controls what suggestions are included or controls for what suggest text terms, suggestions should be suggested. Three possible values can be specified: 

  missing: Only provide suggestions for suggest text terms that are not in the index. This is the default. 

 popular: Only suggest suggestions that occur in more docs than the original suggest text term. 

 always: Suggest any matching suggestions based on terms in the suggest text. 

 Other term suggest options:

  lowercase_terms 

   Lower cases the suggest text terms after text analysis. 

   max_edits 

   The maximum edit distance candidate suggestions can have in order to be considered as a suggestion. Can only be a value between 1 and 2. Any other value result in an bad request error being thrown. Defaults to 2. 

   prefix_length 

   The number of minimal prefix characters that must match in order be a candidate suggestions. Defaults to 1. Increasing this number improves spellcheck performance. Usually misspellings donb t occur in the beginning of terms. (Old name "prefix_len" is deprecated) 

   min_word_length 

   The minimum length a suggest text term must have in order to be included. Defaults to 4. (Old name "min_word_len" is deprecated) 

   shard_size 

   Sets the maximum number of suggestions to be retrieved from each individual shard. During the reduce phase only the top N suggestions are returned based on the size option. Defaults to the size option. Setting this to a value higher than the size can be useful in order to get a more accurate document frequency for spelling corrections at the cost of performance. Due to the fact that terms are partitioned amongst shards, the shard level document frequencies of spelling corrections may not be precise. Increasing this will make these document frequencies more precise. 

   max_inspections 

   A factor that is used to multiply with the shards_size in order to inspect more candidate spell corrections on the shard level. Can improve accuracy at the cost of performance. Defaults to 5. 

   min_doc_freq 

   The minimal threshold in number of documents a suggestion should appear in. This can be specified as an absolute number or as a relative percentage of number of documents. This can improve quality by only suggesting high frequency terms. Defaults to 0f and is not enabled. If a value higher than 1 is specified then the number cannot be fractional. The shard level document frequencies are used for this option. 

   max_term_freq 

   The maximum threshold in number of documents a suggest text token can exist in order to be included. Can be a relative percentage number (e.g 0.4) or an absolute number to represent document frequencies. If an value higher than 1 is specified then fractional can not be specified. Defaults to 0.01f. This can be used to exclude high frequency terms from being spellchecked. High frequency terms are usually spelled correctly on top of this also improves the spellcheck performance. The shard level document frequencies are used for this option. 

   string_distance 

   Which string distance implementation to use for comparing how similar suggested terms are. Five possible values can be specified: internal - The default based on damerau_levenshtein but highly optimized for comparing string distance for terms inside the index. damerau_levenshtein - String distance algorithm based on Damerau-Levenshtein algorithm. levenshtein - String distance algorithm based on Levenshtein edit distance algorithm. jaro_winkler - String distance algorithm based on Jaro-Winkler algorithm. ngram - String distance algorithm based on character n-grams. 

 Phrase Suggester

In order to understand the format of suggestions, please read the Suggesters page first.

The term suggester provides a very convenient API to access word alternatives on a per token basis within a certain string distance. The API allows accessing each token in the stream individually while suggest-selection is left to the API consumer. Yet, often pre-selected suggestions are required in order to present to the end-user. The phrase suggester adds additional logic on top of the term suggester to select entire corrected phrases instead of individual tokens weighted based on ngram-language models. In practice this suggester will be able to make better decisions about which tokens to pick based on co-occurrence and frequencies.

API Example

In general the phrase suggester requires special mapping up front to work. The phrase suggester examples on this page need the following mapping to work. The reverse analyzer is used only in the last example.

Once you have the analyzers and mappings set up you can use the phrase suggester in the same spot youb d use the term suggester:

The response contains suggestions scored by the most likely spell correction first. In this case we received the expected correction "nobel prize".

Basic Phrase suggest API parameters

  field 

   The name of the field used to do n-gram lookups for the language model, the suggester will use this field to gain statistics to score corrections. This field is mandatory. 

   gram_size 

   Sets max size of the n-grams (shingles) in the field. If the field doesnb t contain n-grams (shingles), this should be omitted or set to 1. Note that Elasticsearch tries to detect the gram size based on the specified field. If the field uses a shingle filter, the gram_size is set to the max_shingle_size if not explicitly set. 

   real_word_error_likelihood 

   The likelihood of a term being a misspelled even if the term exists in the dictionary. The default is 0.95, meaning 5% of the real words are misspelled. 

   confidence 

   The confidence level defines a factor applied to the input phrases score which is used as a threshold for other suggest candidates. Only candidates that score higher than the threshold will be included in the result. For instance a confidence level of 1.0 will only return suggestions that score higher than the input phrase. If set to 0.0 the top N candidates are returned. The default is 1.0. 

   max_errors 

   The maximum percentage of the terms considered to be misspellings in order to form a correction. This method accepts a float value in the range [0..1) as a fraction of the actual query terms or a number >=1 as an absolute number of query terms. The default is set to 1.0, meaning only corrections with at most one misspelled term are returned. Note that setting this too high can negatively impact performance. Low values like 1 or 2 are recommended; otherwise the time spend in suggest calls might exceed the time spend in query execution. 

   separator 

   The separator that is used to separate terms in the bigram field. If not set the whitespace character is used as a separator. 

   size 

   The number of candidates that are generated for each individual query term. Low numbers like 3 or 5 typically produce good results. Raising this can bring up terms with higher edit distances. The default is 5. 

   analyzer 

   Sets the analyzer to analyze to suggest text with. Defaults to the search analyzer of the suggest field passed via field. 

   shard_size 

   Sets the maximum number of suggested terms to be retrieved from each individual shard. During the reduce phase, only the top N suggestions are returned based on the size option. Defaults to 5. 

   text 

   Sets the text / query to provide suggestions for. 

   highlight 

   Sets up suggestion highlighting. If not provided then no highlighted field is returned. If provided must contain exactly pre_tag and post_tag, which are wrapped around the changed tokens. If multiple tokens in a row are changed the entire phrase of changed tokens is wrapped rather than each token. 

   collate 

   Checks each suggestion against the specified query to prune suggestions for which no matching docs exist in the index. The collate query for a suggestion is run only on the local shard from which the suggestion has been generated from. The query must be specified and it can be templated, see search templates for more information. The current suggestion is automatically made available as the {{suggestion}} variable, which should be used in your query. You can still specify your own template params b  the suggestion value will be added to the variables you specify. Additionally, you can specify a prune to control if all phrase suggestions will be returned; when set to true the suggestions will have an additional option collate_match, which will be true if matching documents for the phrase was found, false otherwise. The default value for prune is false. 

  

 This query will be run once for every suggestion. 

 

 The {{suggestion}} variable will be replaced by the text of each suggestion. 

 

 An additional field_name variable has been specified in params and is used by the match query. 

 

 All suggestions will be returned with an extra collate_match option indicating whether the generated phrase matched any document. 

Smoothing Models

The phrase suggester supports multiple smoothing models to balance weight between infrequent grams (grams (shingles) are not existing in the index) and frequent grams (appear at least once in the index).

  stupid_backoff 

   A simple backoff model that backs off to lower order n-gram models if the higher order count is 0 and discounts the lower order n-gram model by a constant factor. The default discount is 0.4. Stupid Backoff is the default model. 

   laplace 

   A smoothing model that uses an additive smoothing where a constant (typically 1.0 or smaller) is added to all counts to balance weights. The default alpha is 0.5. 

   linear_interpolation 

   A smoothing model that takes the weighted mean of the unigrams, bigrams, and trigrams based on user supplied weights (lambdas). Linear Interpolation doesnb t have any default values. All parameters (trigram_lambda, bigram_lambda, unigram_lambda) must be supplied. 

 Candidate Generators

The phrase suggester uses candidate generators to produce a list of possible terms per term in the given text. A single candidate generator is similar to a term suggester called for each individual term in the text. The output of the generators is subsequently scored in combination with the candidates from the other terms for suggestion candidates.

Currently only one type of candidate generator is supported, the direct_generator. The Phrase suggest API accepts a list of generators under the key direct_generator; each of the generators in the list is called per term in the original text.

Direct Generators

The direct generators support the following parameters:

  field 

   The field to fetch the candidate suggestions from. This is a required option that either needs to be set globally or per suggestion. 

   size 

   The maximum corrections to be returned per suggest text token. 

   suggest_mode 

   The suggest mode controls what suggestions are included on the suggestions generated on each shard. All values other than always can be thought of as an optimization to generate fewer suggestions to test on each shard and are not rechecked when combining the suggestions generated on each shard. Thus missing will generate suggestions for terms on shards that do not contain them even if other shards do contain them. Those should be filtered out using confidence. Three possible values can be specified: 

  missing: Only generate suggestions for terms that are not in the shard. This is the default. 

 popular: Only suggest terms that occur in more docs on the shard than the original term. 

 always: Suggest any matching suggestions based on terms in the suggest text. 

   max_edits 

   The maximum edit distance candidate suggestions can have in order to be considered as a suggestion. Can only be a value between 1 and 2. Any other value results in a bad request error being thrown. Defaults to 2. 

   prefix_length 

   The number of minimal prefix characters that must match in order be a candidate suggestions. Defaults to 1. Increasing this number improves spellcheck performance. Usually misspellings donb t occur in the beginning of terms. (Old name "prefix_len" is deprecated) 

   min_word_length 

   The minimum length a suggest text term must have in order to be included. Defaults to 4. (Old name "min_word_len" is deprecated) 

   max_inspections 

   A factor that is used to multiply with the shards_size in order to inspect more candidate spelling corrections on the shard level. Can improve accuracy at the cost of performance. Defaults to 5. 

   min_doc_freq 

   The minimal threshold in number of documents a suggestion should appear in. This can be specified as an absolute number or as a relative percentage of number of documents. This can improve quality by only suggesting high frequency terms. Defaults to 0f and is not enabled. If a value higher than 1 is specified, then the number cannot be fractional. The shard level document frequencies are used for this option. 

   max_term_freq 

   The maximum threshold in number of documents in which a suggest text token can exist in order to be included. Can be a relative percentage number (e.g., 0.4) or an absolute number to represent document frequencies. If a value higher than 1 is specified, then fractional can not be specified. Defaults to 0.01f. This can be used to exclude high frequency terms b  which are usually spelled correctly b  from being spellchecked. This also improves the spellcheck performance. The shard level document frequencies are used for this option. 

   pre_filter 

   A filter (analyzer) that is applied to each of the tokens passed to this candidate generator. This filter is applied to the original token before candidates are generated. 

   post_filter 

   A filter (analyzer) that is applied to each of the generated tokens before they are passed to the actual phrase scorer. 

 The following example shows a phrase suggest call with two generators: the first one is using a field containing ordinary indexed terms, and the second one uses a field that uses terms indexed with a reverse filter (tokens are index in reverse order). This is used to overcome the limitation of the direct generators to require a constant prefix to provide high-performance suggestions. The pre_filter and post_filter options accept ordinary analyzer names.

pre_filter and post_filter can also be used to inject synonyms after candidates are generated. For instance for the query captain usq we might generate a candidate usa for the term usq, which is a synonym for america. This allows us to present captain america to the user if this phrase scores high enough.

Completion Suggester

In order to understand the format of suggestions, please read the Suggesters page first.

The completion suggester provides auto-complete/search-as-you-type functionality. This is a navigational feature to guide users to relevant results as they are typing, improving search precision. It is not meant for spell correction or did-you-mean functionality like the term or phrase suggesters.

Ideally, auto-complete functionality should be as fast as a user types to provide instant feedback relevant to what a user has already typed in. Hence, completion suggester is optimized for speed. The suggester uses data structures that enable fast lookups, but are costly to build and are stored in-memory.

Mapping

To use this feature, specify a special mapping for this field, which indexes the field values for fast completions.

Mapping supports the following parameters:

  analyzer 

   The index analyzer to use, defaults to simple. 

   search_analyzer 

   The search analyzer to use, defaults to value of analyzer. 

   preserve_separators 

   Preserves the separators, defaults to true. If disabled, you could find a field starting with Foo Fighters, if you suggest for foof. 

   preserve_position_increments 

   Enables position increments, defaults to true. If disabled and using stopwords analyzer, you could get a field starting with The Beatles, if you suggest for b. Note: You could also achieve this by indexing two inputs, Beatles and The Beatles, no need to change a simple analyzer, if you are able to enrich your data. 

   max_input_length 

   Limits the length of a single input, defaults to 50 UTF-16 code points. This limit is only used at index time to reduce the total number of characters per input string in order to prevent massive inputs from bloating the underlying datastructure. Most use cases wonb t be influenced by the default value since prefix completions seldom grow beyond prefixes longer than a handful of characters. 

 Indexing

You index suggestions like any other field. A suggestion is made of an input and an optional weight attribute. An input is the expected text to be matched by a suggestion query and the weight determines how the suggestions will be scored. Indexing a suggestion is as follows:

The following parameters are supported:

  input 

   The input to store, this can be an array of strings or just a string. This field is mandatory. 

   weight 

   A positive integer or a string containing a positive integer, which defines a weight and allows you to rank your suggestions. This field is optional. 

 You can index multiple suggestions for a document as follows:

You can use the following shorthand form. Note that you can not specify a weight with suggestion(s) in the shorthand form.

Querying

Suggesting works as usual, except that you have to specify the suggest type as completion. Suggestions are near real-time, which means new suggestions can be made visible by refresh and documents once deleted are never shown. This request:

 

 Prefix used to search for suggestions 

 

 Type of suggestions 

 

 Name of the field to search for suggestions in 

returns this response:

_source meta-field must be enabled, which is the default behavior, to enable returning _source with suggestions.

The configured weight for a suggestion is returned as _score. The text field uses the input of your indexed suggestion. Suggestions return the full document _source by default. The size of the _source can impact performance due to disk fetch and network transport overhead. To save some network overhead, filter out unnecessary fields from the _source using source filtering to minimize _source size. Note that the _suggest endpoint doesnb t support source filtering but using suggest on the _search endpoint does:

 

 Filter the source to return only the suggest field 

 

 Name of the field to search for suggestions in 

 

 Number of suggestions to return 

Which should look like:

The basic completion suggester query supports the following parameters:

  field 

   The name of the field on which to run the query (required). 

   size 

   The number of suggestions to return (defaults to 5). 

   skip_duplicates 

   Whether duplicate suggestions should be filtered out (defaults to false). 

 The completion suggester considers all documents in the index. See Context Suggester for an explanation of how to query a subset of documents instead.

In case of completion queries spanning more than one shard, the suggest is executed in two phases, where the last phase fetches the relevant documents from shards, implying executing completion requests against a single shard is more performant due to the document fetch overhead when the suggest spans multiple shards. To get best performance for completions, it is recommended to index completions into a single shard index. In case of high heap usage due to shard size, it is still recommended to break index into multiple shards instead of optimizing for completion performance.

Skip duplicate suggestions

Queries can return duplicate suggestions coming from different documents. It is possible to modify this behavior by setting skip_duplicates to true. When set, this option filters out documents with duplicate suggestions from the result.

When set to true, this option can slow down search because more suggestions need to be visited to find the top N.

Fuzzy queries

The completion suggester also supports fuzzy queries b  this means you can have a typo in your search and still get results back.

Suggestions that share the longest prefix to the query prefix will be scored higher.

The fuzzy query can take specific fuzzy parameters. The following parameters are supported:

  fuzziness 

   The fuzziness factor, defaults to AUTO. See Fuzziness

 for allowed settings. 

   transpositions 

   if set to true, transpositions are counted as one change instead of two, defaults to true 

   min_length 

   Minimum length of the input before fuzzy suggestions are returned, defaults 3 

   prefix_length 

   Minimum length of the input, which is not checked for fuzzy alternatives, defaults to 1 

   unicode_aware 

   If true, all measurements (like fuzzy edit distance, transpositions, and lengths) are measured in Unicode code points instead of in bytes. This is slightly slower than raw bytes, so it is set to false by default. 

 If you want to stick with the default values, but still use fuzzy, you can either use fuzzy: {} or fuzzy: true.

Regex queries

The completion suggester also supports regex queries meaning you can express a prefix as a regular expression

The regex query can take specific regex parameters. The following parameters are supported:

  flags 

   Possible flags are ALL (default), ANYSTRING, COMPLEMENT, EMPTY, INTERSECTION, INTERVAL, or NONE. See regexp-syntax for their meaning 

   max_determinized_states 

   Regular expressions are dangerous because itb s easy to accidentally create an innocuous looking one that requires an exponential number of internal determinized automaton states (and corresponding RAM and CPU) for Lucene to execute. Lucene prevents these using the max_determinized_states setting (defaults to 10000). You can raise this limit to allow more complex regular expressions to execute. 

 Context Suggester

The completion suggester considers all documents in the index, but it is often desirable to serve suggestions filtered and/or boosted by some criteria. For example, you want to suggest song titles filtered by certain artists or you want to boost song titles based on their genre.

To achieve suggestion filtering and/or boosting, you can add context mappings while configuring a completion field. You can define multiple context mappings for a completion field. Every context mapping has a unique name and a type. There are two types: category and geo. Context mappings are configured under the contexts parameter in the field mapping.

It is mandatory to provide a context when indexing and querying a context enabled completion field.

The following defines types, each with two context mappings for a completion field:

 

 Defines a category context named place_type where the categories must be sent with the suggestions. 

 

 Defines a geo context named location where the categories must be sent with the suggestions. 

 

 Defines a category context named place_type where the categories are read from the cat field. 

 

 Defines a geo context named location where the categories are read from the loc field. 

Adding context mappings increases the index size for completion field. The completion index is entirely heap resident, you can monitor the completion field index size using Indices Stats.

Category Context

The category context allows you to associate one or more categories with suggestions at index time. At query time, suggestions can be filtered and boosted by their associated categories.

The mappings are set up like the place_type fields above. If path is defined then the categories are read from that path in the document, otherwise they must be sent in the suggest field like this:

 

 These suggestions will be associated with cafe and food category. 

If the mapping had a path then the following index request would be enough to add the categories:

 

 These suggestions will be associated with cafe and food category. 

If context mapping references another field and the categories are explicitly indexed, the suggestions are indexed with both set of categories.

Category Query

Suggestions can be filtered by one or more categories. The following filters suggestions by multiple categories:

If multiple categories or category contexts are set on the query they are merged as a disjunction. This means that suggestions match if they contain at least one of the provided context values.

Suggestions with certain categories can be boosted higher than others. The following filters suggestions by categories and additionally boosts suggestions associated with some categories:

 

 The context query filter suggestions associated with categories cafe and restaurants and boosts the suggestions associated with restaurants by a factor of 2 

In addition to accepting category values, a context query can be composed of multiple category context clauses. The following parameters are supported for a category context clause:

  context 

   The value of the category to filter/boost on. This is mandatory. 

   boost 

   The factor by which the score of the suggestion should be boosted, the score is computed by multiplying the boost with the suggestion weight, defaults to 1 

   prefix 

   Whether the category value should be treated as a prefix or not. For example, if set to true, you can filter category of type1, type2 and so on, by specifying a category prefix of type. Defaults to false 

 If a suggestion entry matches multiple contexts the final score is computed as the maximum score produced by any matching contexts.

Geo location Context

A geo context allows you to associate one or more geo points or geohashes with suggestions at index time. At query time, suggestions can be filtered and boosted if they are within a certain distance of a specified geo location.

Internally, geo points are encoded as geohashes with the specified precision.

Geo Mapping

In addition to the path setting, geo context mapping accepts the following settings:

  precision 

   This defines the precision of the geohash to be indexed and can be specified as a distance value (5m, 10km etc.), or as a raw geohash precision (1..12). Defaults to a raw geohash precision value of 6. 

 The index time precision setting sets the maximum geohash precision that can be used at query time.

Indexing geo contexts

geo contexts can be explicitly set with suggestions or be indexed from a geo point field in the document via the path parameter, similar to category contexts. Associating multiple geo location context with a suggestion, will index the suggestion for every geo location. The following indexes a suggestion with two geo location contexts:

Geo location Query

Suggestions can be filtered and boosted with respect to how close they are to one or more geo points. The following filters suggestions that fall within the area represented by the encoded geohash of a geo point:

When a location with a lower precision at query time is specified, all suggestions that fall within the area will be considered.

If multiple categories or category contexts are set on the query they are merged as a disjunction. This means that suggestions match if they contain at least one of the provided context values.

Suggestions that are within an area represented by a geohash can also be boosted higher than others, as shown by the following:

 

 The context query filters for suggestions that fall under the geo location represented by a geohash of (43.662, -79.380) with a precision of 2 and boosts suggestions that fall under the geohash representation of (43.6624803, -79.3863353) with a default precision of 6 by a factor of 2 

If a suggestion entry matches multiple contexts the final score is computed as the maximum score produced by any matching contexts.

In addition to accepting context values, a context query can be composed of multiple context clauses. The following parameters are supported for a category context clause:

  context 

   A geo point object or a geo hash string to filter or boost the suggestion by. This is mandatory. 

   boost 

   The factor by which the score of the suggestion should be boosted, the score is computed by multiplying the boost with the suggestion weight, defaults to 1 

   precision 

   The precision of the geohash to encode the query geo point. This can be specified as a distance value (5m, 10km etc.), or as a raw geohash precision (1..12). Defaults to index time precision level. 

   neighbours 

   Accepts an array of precision values at which neighbouring geohashes should be taken into account. precision value can be a distance value (5m, 10km etc.) or a raw geohash precision (1..12). Defaults to generating neighbours for index time precision level. 

 Returning the type of the suggester

Sometimes you need to know the exact type of a suggester in order to parse its results. The typed_keys parameter can be used to change the suggesterb s name in the response so that it will be prefixed by its type.

Considering the following example with two suggesters term and phrase:

In the response, the suggester names will be changed to respectively term#my-first-suggester and phrase#my-second-suggester, reflecting the types of each suggestion:

 

 The name my-first-suggester now contains the term prefix. 

 

 The name my-second-suggester now contains the phrase prefix. 

Multi Search API

The multi search API allows to execute several search requests within the same API. The endpoint for it is _msearch.

The format of the request is similar to the bulk API format and makes use of the newline delimited JSON (NDJSON) format. The structure is as follows (the structure is specifically optimized to reduce parsing if a specific search ends up redirected to another node):

NOTE: the final line of data must end with a newline character \n. Each newline character may be preceded by a carriage return \r. When sending requests to this endpoint the Content-Type header should be set to application/x-ndjson.

The header part includes which index / indices to search on, the search_type, preference, and routing. The body includes the typical search body request (including the query, aggregations, from, size, and so on). Here is an example:

Note, the above includes an example of an empty header (can also be just without any content) which is supported as well.

The response returns a responses array, which includes the search response and status code for each search request matching its order in the original multi search request. If there was a complete failure for that specific search request, an object with error message and corresponding status code will be returned in place of the actual search response.

The endpoint allows to also search against an index/indices in the URI itself, in which case it will be used as the default unless explicitly defined otherwise in the header. For example:

The above will execute the search against the twitter index for all the requests that donb t define an index, and the last one will be executed against the twitter2 index.

The search_type can be set in a similar manner to globally apply to all search requests.

The msearchb s max_concurrent_searches request parameter can be used to control the maximum number of concurrent searches the multi search api will execute. This default is based on the number of data nodes and the default search thread pool size.

The request parameter max_concurrent_shard_requests can be used to control the maximum number of concurrent shard requests the each sub search request will execute. This parameter should be used to protect a single request from overloading a cluster (e.g., a default request will hit all indices in a cluster which could cause shard request rejections if the number of shards per node is high). This default is based on the number of data nodes in the cluster but at most 256.In certain scenarios parallelism isnb t achieved through concurrent request such that this protection will result in poor performance. For instance in an environment where only a very low number of concurrent search requests are expected it might help to increase this value to a higher number.

Security

See URL-based access control

Template support

Much like described in Search Template for the _search resource, _msearch also provides support for templates. Submit them like follows:

for inline templates.

You can also create search templates:

and later use them in a _msearch:

Count API

The count API allows to easily execute a query and get the number of matches for that query. It can be executed across one or more indices. The query can either be provided using a simple query string as a parameter, or using the Query DSL defined within the request body. Here is an example:

The query being sent in the body must be nested in a query key, same as the search api works

Both examples above do the same thing, which is count the number of tweets from the twitter index for a certain user. The result is:

The query is optional, and when not provided, it will use match_all to count all the docs.

Multi index

The count API can be applied to multiple indices.

Request Parameters

When executing count using the query parameter q, the query passed is a query string using Lucene query parser. There are additional parameters that can be passed:

Name Descriptiondf

The default field to use when no field prefix is defined within the query.

analyzer

The analyzer name to be used when analyzing the query string.

default_operator

The default operator to be used, can be AND or OR. Defaults to OR.

lenient

If set to true will cause format based failures (like providing text to a numeric field) to be ignored. Defaults to false.

analyze_wildcard

Should wildcard and prefix queries be analyzed or not. Defaults to false.

terminate_after

The maximum count for each shard, upon reaching which the query execution will terminate early. If set, the response will have a boolean field terminated_early to indicate whether the query execution has actually terminated_early. Defaults to no terminate_after.

Request Body

The count can use the Query DSL within its body in order to express the query that should be executed. The body content can also be passed as a REST parameter named source.

Both HTTP GET and HTTP POST can be used to execute count with body. Since not all clients support GET with body, POST is allowed as well.

Distributed

The count operation is broadcast across all shards. For each shard id group, a replica is chosen and executed against it. This means that replicas increase the scalability of count.

Routing

The routing value (a comma separated list of the routing values) can be specified to control which shards the count request will be executed on.

Validate API

The validate API allows a user to validate a potentially expensive query without executing it. Web ll use the following test data to explain _validate:

When sent a valid query:

The response contains valid:true:

Request Parameters

When executing exists using the query parameter q, the query passed is a query string using Lucene query parser. There are additional parameters that can be passed:

Name Descriptiondf

The default field to use when no field prefix is defined within the query.

analyzer

The analyzer name to be used when analyzing the query string.

default_operator

The default operator to be used, can be AND or OR. Defaults to OR.

lenient

If set to true will cause format based failures (like providing text to a numeric field) to be ignored. Defaults to false.

analyze_wildcard

Should wildcard and prefix queries be analyzed or not. Defaults to false.

The query may also be sent in the request body:

The query being sent in the body must be nested in a query key, same as the search api works

If the query is invalid, valid will be false. Here the query is invalid because Elasticsearch knows the post_date field should be a date due to dynamic mapping, and foo does not correctly parse into a date:

An explain parameter can be specified to get more detailed information about why a query failed:

responds with:

When the query is valid, the explanation defaults to the string representation of that query. With rewrite set to true, the explanation is more detailed showing the actual Lucene query that will be executed.

For More Like This:

Response:

By default, the request is executed on a single shard only, which is randomly selected. The detailed explanation of the query may depend on which shard is being hit, and therefore may vary from one request to another. So, in case of query rewrite the all_shards parameter should be used to get response from all available shards.

For Fuzzy Queries:

Response:

Explain API

The explain api computes a score explanation for a query and a specific document. This can give useful feedback whether a document matches or didnb t match a specific query.

Note that a single index must be provided to the index parameter.

Usage

Full query example:

This will yield the following result:

There is also a simpler way of specifying the query via the q parameter. The specified q parameter value is then parsed as if the query_string query was used. Example usage of the q parameter in the explain api:

This will yield the same result as the previous request.

All parameters:

  _source 

   Set to true to retrieve the _source of the document explained. You can also retrieve part of the document by using _source_includes & _source_excludes (see Get API for more details) 

   stored_fields 

   Allows to control which stored fields to return as part of the document explained. 

   routing 

   Controls the routing in the case the routing was used during indexing. 

   parent 

   Same effect as setting the routing parameter. 

   preference 

   Controls on which shard the explain is executed. 

   source 

   Allows the data of the request to be put in the query string of the url. 

   q 

   The query string (maps to the query_string query). 

   df 

   The default field to use when no field prefix is defined within the query. 

   analyzer 

   The analyzer name to be used when analyzing the query string. Defaults to the default search analyzer. 

   analyze_wildcard 

   Should wildcard and prefix queries be analyzed or not. Defaults to false. 

   lenient 

   If set to true will cause format based failures (like providing text to a numeric field) to be ignored. Defaults to false. 

   default_operator 

   The default operator to be used, can be AND or OR. Defaults to OR. 

 Profile API

The Profile API is a debugging tool and adds significant overhead to search execution.

The Profile API provides detailed timing information about the execution of individual components in a search request. It gives the user insight into how search requests are executed at a low level so that the user can understand why certain requests are slow, and take steps to improve them. Note that the Profile API, amongst other things, doesnb t measure network latency, time spent in the search fetch phase, time spent while the requests spends in queues or while merging shard responses on the coordinating node.

The output from the Profile API is very verbose, especially for complicated requests executed across many shards. Pretty-printing the response is recommended to help understand the output

Usage

Any _search request can be profiled by adding a top-level profile parameter:

 

 Setting the top-level profile parameter to true will enable profiling for the search 

This will yield the following result:

 

 Search results are returned, but were omitted here for brevity 

Even for a simple query, the response is relatively complicated. Letb s break it down piece-by-piece before moving to more complex examples.

First, the overall structure of the profile response is as follows:

 

 A profile is returned for each shard that participated in the response, and is identified by a unique ID 

 

 Each profile contains a section which holds details about the query execution 

 

 Each profile has a single time representing the cumulative rewrite time 

 

 Each profile also contains a section about the Lucene Collectors which run the search 

 

 Each profile contains a section which holds the details about the aggregation execution 

Because a search request may be executed against one or more shards in an index, and a search may cover one or more indices, the top level element in the profile response is an array of shard objects. Each shard object lists its id which uniquely identifies the shard. The IDb s format is [nodeID][indexName][shardID].

The profile itself may consist of one or more "searches", where a search is a query executed against the underlying Lucene index. Most search requests submitted by the user will only execute a single search against the Lucene index. But occasionally multiple searches will be executed, such as including a global aggregation (which needs to execute a secondary "match_all" query for the global context).

Inside each search object there will be two arrays of profiled information: a query array and a collector array. Alongside the search object is an aggregations object that contains the profile information for the aggregations. In the future, more sections may be added, such as suggest, highlight, etc.

There will also be a rewrite metric showing the total time spent rewriting the query (in nanoseconds).

As with other statistics apis, the Profile API supports human readable outputs. This can be turned on by adding ?human=true to the query string. In this case, the output contains the additional time field containing rounded, human readable timing information (e.g. "time": "391,9ms", "time": "123.3micros").

Profiling Queries

The details provided by the Profile API directly expose Lucene class names and concepts, which means that complete interpretation of the results require fairly advanced knowledge of Lucene. This page attempts to give a crash-course in how Lucene executes queries so that you can use the Profile API to successfully diagnose and debug queries, but it is only an overview. For complete understanding, please refer to Luceneb s documentation and, in places, the code.

With that said, a complete understanding is often not required to fix a slow query. It is usually sufficient to see that a particular component of a query is slow, and not necessarily understand why the advance phase of that query is the cause, for example.

query Section

The query section contains detailed timing of the query tree executed by Lucene on a particular shard. The overall structure of this query tree will resemble your original Elasticsearch query, but may be slightly (or sometimes very) different. It will also use similar but not always identical naming. Using our previous match query example, letb s analyze the query section:

 

 The breakdown timings are omitted for simplicity 

Based on the profile structure, we can see that our match query was rewritten by Lucene into a BooleanQuery with two clauses (both holding a TermQuery). The type field displays the Lucene class name, and often aligns with the equivalent name in Elasticsearch. The description field displays the Lucene explanation text for the query, and is made available to help differentiating between parts of your query (e.g. both message:search and message:test are TermQueryb s and would appear identical otherwise.

The time_in_nanos field shows that this query took ~1.8ms for the entire BooleanQuery to execute. The recorded time is inclusive of all children.

The breakdown field will give detailed stats about how the time was spent, web ll look at that in a moment. Finally, the children array lists any sub-queries that may be present. Because we searched for two values ("search test"), our BooleanQuery holds two children TermQueries. They have identical information (type, time, breakdown, etc). Children are allowed to have their own children.

Timing Breakdown

The breakdown component lists detailed timing statistics about low-level Lucene execution:

Timings are listed in wall-clock nanoseconds and are not normalized at all. All caveats about the overall time_in_nanos apply here. The intention of the breakdown is to give you a feel for A) what machinery in Lucene is actually eating time, and B) the magnitude of differences in times between the various components. Like the overall time, the breakdown is inclusive of all children times.

The meaning of the stats are as follows:

All parameters:

  create_weight 

   A Query in Lucene must be capable of reuse across multiple IndexSearchers (think of it as the engine that executes a search against a specific Lucene Index). This puts Lucene in a tricky spot, since many queries need to accumulate temporary state/statistics associated with the index it is being used against, but the Query contract mandates that it must be immutable. To get around this, Lucene asks each query to generate a Weight object which acts as a temporary context object to hold state associated with this particular (IndexSearcher, Query) tuple. The weight metric shows how long this process takes 

   build_scorer 

   This parameter shows how long it takes to build a Scorer for the query. A Scorer is the mechanism that iterates over matching documents and generates a score per-document (e.g. how well does "foo" match the document?). Note, this records the time required to generate the Scorer object, not actually score the documents. Some queries have faster or slower initialization of the Scorer, depending on optimizations, complexity, etc. This may also show timing associated with caching, if enabled and/or applicable for the query 

   next_doc 

   The Lucene method next_doc returns Doc ID of the next document matching the query. This statistic shows the time it takes to determine which document is the next match, a process that varies considerably depending on the nature of the query. Next_doc is a specialized form of advance() which is more convenient for many queries in Lucene. It is equivalent to advance(docId() + 1) 

   advance 

   advance is the "lower level" version of next_doc: it serves the same purpose of finding the next matching doc, but requires the calling query to perform extra tasks such as identifying and moving past skips, etc. However, not all queries can use next_doc, so advance is also timed for those queries. Conjunctions (e.g. must clauses in a boolean) are typical consumers of advance 

   matches 

   Some queries, such as phrase queries, match documents using a "two-phase" process. First, the document is "approximately" matched, and if it matches approximately, it is checked a second time with a more rigorous (and expensive) process. The second phase verification is what the matches statistic measures. For example, a phrase query first checks a document approximately by ensuring all terms in the phrase are present in the doc. If all the terms are present, it then executes the second phase verification to ensure the terms are in-order to form the phrase, which is relatively more expensive than just checking for presence of the terms. Because this two-phase process is only used by a handful of queries, the metric statistic will often be zero 

   score 

   This records the time taken to score a particular document via its Scorer 

   *_count 

   Records the number of invocations of the particular method. For example, "next_doc_count": 2, means the nextDoc() method was called on two different documents. This can be used to help judge how selective queries are, by comparing counts between different query components. 

 collectors Section

The Collectors portion of the response shows high-level execution details. Lucene works by defining a "Collector" which is responsible for coordinating the traversal, scoring, and collection of matching documents. Collectors are also how a single query can record aggregation results, execute unscoped "global" queries, execute post-query filters, etc.

Looking at the previous example:

We see a single collector named SimpleTopScoreDocCollector wrapped into CancellableCollector. SimpleTopScoreDocCollector is the default "scoring and sorting" Collector used by Elasticsearch. The reason field attempts to give a plain English description of the class name. The time_in_nanos is similar to the time in the Query tree: a wall-clock time inclusive of all children. Similarly, children lists all sub-collectors. The CancellableCollector that wraps SimpleTopScoreDocCollector is used by Elasticsearch to detect if the current search was cancelled and stop collecting documents as soon as it occurs.

It should be noted that Collector times are independent from the Query times. They are calculated, combined, and normalized independently! Due to the nature of Luceneb s execution, it is impossible to "merge" the times from the Collectors into the Query section, so they are displayed in separate portions.

For reference, the various collector reasons are:

  search_sorted 

   A collector that scores and sorts documents. This is the most common collector and will be seen in most simple searches 

   search_count 

   A collector that only counts the number of documents that match the query, but does not fetch the source. This is seen when size: 0 is specified 

   search_terminate_after_count 

   A collector that terminates search execution after n matching documents have been found. This is seen when the terminate_after_count query parameter has been specified 

   search_min_score 

   A collector that only returns matching documents that have a score greater than n. This is seen when the top-level parameter min_score has been specified. 

   search_multi 

   A collector that wraps several other collectors. This is seen when combinations of search, aggregations, global aggs, and post_filters are combined in a single search. 

   search_timeout 

   A collector that halts execution after a specified period of time. This is seen when a timeout top-level parameter has been specified. 

   aggregation 

   A collector that Elasticsearch uses to run aggregations against the query scope. A single aggregation collector is used to collect documents for all aggregations, so you will see a list of aggregations in the name rather. 

   global_aggregation 

   A collector that executes an aggregation against the global query scope, rather than the specified query. Because the global scope is necessarily different from the executed query, it must execute its own match_all query (which you will see added to the Query section) to collect your entire dataset 

 rewrite Section

All queries in Lucene undergo a "rewriting" process. A query (and its sub-queries) may be rewritten one or more times, and the process continues until the query stops changing. This process allows Lucene to perform optimizations, such as removing redundant clauses, replacing one query for a more efficient execution path, etc. For example a Boolean b Boolean b TermQuery can be rewritten to a TermQuery, because all the Booleans are unnecessary in this case.

The rewriting process is complex and difficult to display, since queries can change drastically. Rather than showing the intermediate results, the total rewrite time is simply displayed as a value (in nanoseconds). This value is cumulative and contains the total time for all queries being rewritten.

A more complex example

To demonstrate a slightly more complex query and the associated results, we can profile the following query:

This example has:

 A query 

 A scoped aggregation 

 A global aggregation 

 A post_filter 

And the response:

 

 The "aggregations" portion has been omitted because it will be covered in the next section 

As you can see, the output is significantly more verbose than before. All the major portions of the query are represented:

 The first TermQuery (user:test) represents the main term query 

 The second TermQuery (message:some) represents the post_filter query 

The Collector tree is fairly straightforward, showing how a single CancellableCollector wraps a MultiCollector which also wraps a FilteredCollector to execute the post_filter (and in turn wraps the normal scoring SimpleCollector), a BucketCollector to run all scoped aggregations.

Understanding MultiTermQuery output

A special note needs to be made about the MultiTermQuery class of queries. This includes wildcards, regex, and fuzzy queries. These queries emit very verbose responses, and are not overly structured.

Essentially, these queries rewrite themselves on a per-segment basis. If you imagine the wildcard query b*, it technically can match any token that begins with the letter "b". It would be impossible to enumerate all possible combinations, so Lucene rewrites the query in context of the segment being evaluated, e.g., one segment may contain the tokens [bar, baz], so the query rewrites to a BooleanQuery combination of "bar" and "baz". Another segment may only have the token [bakery], so the query rewrites to a single TermQuery for "bakery".

Due to this dynamic, per-segment rewriting, the clean tree structure becomes distorted and no longer follows a clean "lineage" showing how one query rewrites into the next. At present time, all we can do is apologize, and suggest you collapse the details for that queryb s children if it is too confusing. Luckily, all the timing statistics are correct, just not the physical layout in the response, so it is sufficient to just analyze the top-level MultiTermQuery and ignore its children if you find the details too tricky to interpret.

Hopefully this will be fixed in future iterations, but it is a tricky problem to solve and still in-progress :)

Profiling Aggregations

aggregations Section

The aggregations section contains detailed timing of the aggregation tree executed by a particular shard. The overall structure of this aggregation tree will resemble your original Elasticsearch request. Letb s execute the previous query again and look at the aggregation profile this time:

This yields the following aggregation profile output:

From the profile structure we can see that the my_scoped_agg is internally being run as a LongTermsAggregator (because the field it is aggregating, likes, is a numeric field). At the same level, we see a GlobalAggregator which comes from my_global_agg. That aggregation then has a child LongTermsAggregator which comes from the second termb s aggregation on likes.

The time_in_nanos field shows the time executed by each aggregation, and is inclusive of all children. While the overall time is useful, the breakdown field will give detailed stats about how the time was spent.

Timing Breakdown

The breakdown component lists detailed timing statistics about low-level Lucene execution:

Timings are listed in wall-clock nanoseconds and are not normalized at all. All caveats about the overall time apply here. The intention of the breakdown is to give you a feel for A) what machinery in Elasticsearch is actually eating time, and B) the magnitude of differences in times between the various components. Like the overall time, the breakdown is inclusive of all children times.

The meaning of the stats are as follows:

All parameters:

  initialise 

   This times how long it takes to create and initialise the aggregation before starting to collect documents. 

   collect 

   This represents the cumulative time spent in the collect phase of the aggregation. This is where matching documents are passed to the aggregation and the state of the aggregator is updated based on the information contained in the documents. 

   build_aggregation 

   This represents the time spent creating the shard level results of the aggregation ready to pass back to the reducing node after the collection of documents is finished. 

   reduce 

   This is not currently used and will always report 0. Currently aggregation profiling only times the shard level parts of the aggregation execution. Timing of the reduce phase will be added later. 

   *_count 

   Records the number of invocations of the particular method. For example, "collect_count": 2, means the collect() method was called on two different documents. 

 Profiling Considerations

Performance Notes

Like any profiler, the Profile API introduces a non-negligible overhead to search execution. The act of instrumenting low-level method calls such as collect, advance, and next_doc can be fairly expensive, since these methods are called in tight loops. Therefore, profiling should not be enabled in production settings by default, and should not be compared against non-profiled query times. Profiling is just a diagnostic tool.

There are also cases where special Lucene optimizations are disabled, since they are not amenable to profiling. This could cause some queries to report larger relative times than their non-profiled counterparts, but in general should not have a drastic effect compared to other components in the profiled query.

Limitations

 Profiling currently does not measure the search fetch phase nor the network overhead 

 Profiling also does not account for time spent in the queue, merging shard responses on the coordinating node, or additional work such as building global ordinals (an internal data structure used to speed up search) 

 Profiling statistics are currently not available for suggestions, highlighting, dfs_query_then_fetch 

 Profiling of the reduce phase of aggregation is currently not available 

 The Profiler is still highly experimental. The Profiler is instrumenting parts of Lucene that were never designed to be exposed in this manner, and so all results should be viewed as a best effort to provide detailed diagnostics. We hope to improve this over time. If you find obviously wrong numbers, strange query structures, or other bugs, please report them! 

Field Capabilities API

The field capabilities API allows to retrieve the capabilities of fields among multiple indices.

The field capabilities API by default executes on all indices:

The request can also be restricted to specific indices:

Supported request options:

  fields 

   A list of fields to compute stats for. The field name supports wildcard notation. For example, using text_* will cause all fields that match the expression to be returned. 

 Field Capabilities

The field capabilities API returns the following information per field:

  searchable 

   Whether this field is indexed for search on all indices. 

   aggregatable 

   Whether this field can be aggregated on all indices. 

   indices 

   The list of indices where this field has the same type, or null if all indices have the same type for the field. 

   non_searchable_indices 

   The list of indices where this field is not searchable, or null if all indices have the same definition for the field. 

   non_aggregatable_indices 

   The list of indices where this field is not aggregatable, or null if all indices have the same definition for the field. 

 Response format

Request:

 

 The field rating is defined as a long in index1 and index2 and as a keyword in index3 and index4. 

 

 The field rating is not aggregatable in index1. 

 

 The field rating is not searchable in index4. 

 

 The field title is defined as text in all indices. 

Ranking Evaluation API

 The ranking evaluation API is experimental and may be changed or removed completely in a future release, as well as change in non-backwards compatible ways on minor versions updates. Elastic will take a best effort approach to fix any issues, but experimental features are not subject to the support SLA of official GA features. 

The ranking evaluation API allows to evaluate the quality of ranked search results over a set of typical search queries. Given this set of queries and a list of manually rated documents, the _rank_eval endpoint calculates and returns typical information retrieval metrics like mean reciprocal rank, precision or discounted cumulative gain.

Overview

Search quality evaluation starts with looking at the users of your search application, and the things that they are searching for. Users have a specific information need, e.g. they are looking for gift in a web shop or want to book a flight for their next holiday. They usually enters some search terms into a search box or some other web form. All of this information, together with meta information about the user (e.g. the browser, location, earlier preferences etcb &) then gets translated into a query to the underlying search system.

The challenge for search engineers is to tweak this translation process from user entries to a concrete query in such a way, that the search results contain the most relevant information with respect to the users information need. This can only be done if the search result quality is evaluated constantly across a representative test suite of typical user queries, so that improvements in the rankings for one particular query doesnb t negatively effect the ranking for other types of queries.

In order to get started with search quality evaluation, three basic things are needed:

 a collection of documents you want to evaluate your query performance against, usually one or more indices 

 a collection of typical search requests that users enter into your system 

 a set of document ratings that judge the documents relevance with respect to a search request+ It is important to note that one set of document ratings is needed per test query, and that the relevance judgements are based on the information need of the user that entered the query. 

The ranking evaluation API provides a convenient way to use this information in a ranking evaluation request to calculate different search evaluation metrics. This gives a first estimation of your overall search quality and give you a measurement to optimize against when fine-tuning various aspect of the query generation in your application.

Ranking evaluation request structure

In its most basic form, a request to the _rank_eval endpoint has two sections:

 

 a set of typical search requests, together with their provided ratings 

 

 definition of the evaluation metric to calculate 

 

 a specific metric and its parameters 

The request section contains several search requests typical to your application, along with the document ratings for each particular search request, e.g.

 

 the search requests id, used to group result details later 

 

 the query that is being evaluated 

 

 a list of document ratings, each entry containing the documents _index and _id together with the rating of the documents relevance with regards to this search request 

A document rating can be any integer value that expresses the relevance of the document on a user defined scale. For some of the metrics, just giving a binary rating (e.g. 0 for irrelevant and 1 for relevant) will be sufficient, other metrics can use a more fine grained scale.

Template based ranking evaluation

As an alternative to having to provide a single query per test request, it is possible to specify query templates in the evaluation request and later refer to them. Queries with similar structure that only differ in their parameters donb t have to be repeated all the time in the requests section this way. In typical search systems where user inputs usually get filled into a small set of query templates, this helps making the evaluation request more succinct.

 

 the template id 

 

 the template definition to use 

 

 a reference to a previously defined template 

 

 the parameters to use to fill the template 

Available evaluation metrics

The metric section determines which of the available evaluation metrics is going to be used. Currently, the following metrics are supported:

Precision at K (P@k)

This metric measures the number of relevant results in the top k search results. Its a form of the well known Precision metric that only looks at the top k documents. It is the fraction of relevant documents in those first k search. A precision at 10 (P@10) value of 0.6 then means six out of the 10 top hits are relevant with respect to the users information need.

P@k works well as a simple evaluation metric that has the benefit of being easy to understand and explain. Documents in the collection need to be rated either as relevant or irrelevant with respect to the current query. P@k does not take into account where in the top k results the relevant documents occur, so a ranking of ten results that contains one relevant result in position 10 is equally good as a ranking of ten results that contains one relevant result in position 1.

The precision metric takes the following optional parameters

Parameter Descriptionk

sets the maximum number of documents retrieved per query. This value will act in place of the usual size parameter in the query. Defaults to 10.

relevant_rating_threshold

sets the rating threshold above which documents are considered to be "relevant". Defaults to 1.

ignore_unlabeled

controls how unlabeled documents in the search results are counted. If set to true, unlabeled documents are ignored and neither count as relevant or irrelevant. Set to false (the default), they are treated as irrelevant.

Mean reciprocal rank

For every query in the test suite, this metric calculates the reciprocal of the rank of the first relevant document. For example finding the first relevant result in position 3 means the reciprocal rank is 1/3. The reciprocal rank for each query is averaged across all queries in the test suite to give the mean reciprocal rank.

The mean_reciprocal_rank metric takes the following optional parameters

Parameter Descriptionk

sets the maximum number of documents retrieved per query. This value will act in place of the usual size parameter in the query. Defaults to 10.

relevant_rating_threshold

Sets the rating threshold above which documents are considered to be "relevant". Defaults to 1.

Discounted cumulative gain (DCG)

In contrast to the two metrics above, discounted cumulative gain takes both, the rank and the rating of the search results, into account.

The assumption is that highly relevant documents are more useful for the user when appearing at the top of the result list. Therefore, the DCG formula reduces the contribution that high ratings for documents on lower search ranks have on the overall DCG metric.

The dcg metric takes the following optional parameters:

Parameter Descriptionk

sets the maximum number of documents retrieved per query. This value will act in place of the usual size parameter in the query. Defaults to 10.

normalize

If set to true, this metric will calculate the Normalized DCG.

Expected Reciprocal Rank (ERR)

Expected Reciprocal Rank (ERR) is an extension of the classical reciprocal rank for the graded relevance case (Olivier Chapelle, Donald Metzler, Ya Zhang, and Pierre Grinspan. 2009. Expected reciprocal rank for graded relevance.)

It is based on the assumption of a cascade model of search, in which a user scans through ranked search results in order and stops at the first document that satisfies the information need. For this reason, it is a good metric for question answering and navigation queries, but less so for survey oriented information needs where the user is interested in finding many relevant documents in the top k results.

The metric models the expectation of the reciprocal of the position at which a user stops reading through the result list. This means that relevant document in top ranking positions will contribute much to the overall score. However, the same document will contribute much less to the score if it appears in a lower rank, even more so if there are some relevant (but maybe less relevant) documents preceding it. In this way, the ERR metric discounts documents which are shown after very relevant documents. This introduces a notion of dependency in the ordering of relevant documents that e.g. Precision or DCG donb t account for.

The expected_reciprocal_rank metric takes the following parameters:

Parameter Descriptionmaximum_relevance

Mandatory parameter. The highest relevance grade used in the user supplied relevance judgments.

k

sets the maximum number of documents retrieved per query. This value will act in place of the usual size parameter in the query. Defaults to 10.

Response format

The response of the _rank_eval endpoint contains the overall calculated result for the defined quality metric, a details section with a breakdown of results for each query in the test suite and an optional failures section that shows potential errors of individual queries. The response has the following format:

 

 the overall evaluation quality calculated by the defined metric 

 

 the details section contains one entry for every query in the original requests section, keyed by the search request id 

 

 the metric_score in the details section shows the contribution of this query to the global quality metric score 

 

 the unrated_docs section contains an _index and _id entry for each document in the search result for this query that didnb t have a ratings value. This can be used to ask the user to supply ratings for these documents 

 

 the hits section shows a grouping of the search results with their supplied rating 

 

 the metric_details give additional information about the calculated quality metric (e.g. how many of the retrieved documents where relevant). The content varies for each metric but allows for better interpretation of the results 

'''

from metrics import f1_score
from metrics import classification_report

from data_loader import DataLoader
import utils

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default='data/msra/', help="Directory containing the dataset")
parser.add_argument('--bert_model_dir', default='bert-base-chinese-pytorch', help="Directory containing the BERT model in PyTorch")
parser.add_argument('--model_dir', default='experiments/base_model', help="Directory containing params.json")
parser.add_argument('--seed', type=int, default=23, help="random seed for initialization")
parser.add_argument('--restore_file', default='best', help="name of the file in `model_dir` containing weights to load")
parser.add_argument('--multi_gpu', default=False, action='store_true', help="Whether to use multiple GPUs if available")
parser.add_argument('--fp16', default=False, action='store_true', help="Whether to use 16-bit float precision instead of 32-bit")


def evaluate(model, data_iterator, params, mark='Eval', verbose=False):
    """Evaluate the model on `steps` batches."""
    # set model to evaluation mode
    model.eval()

    idx2tag = params.idx2tag

    true_tags = []
    pred_tags = []

    # a running average object for loss
    loss_avg = utils.RunningAverage()

    for _ in range(params.eval_steps):
        # fetch the next evaluation batch
        batch_data, batch_tags = next(data_iterator)
        batch_masks = batch_data.gt(0)

        loss = model(batch_data, token_type_ids=None, attention_mask=batch_masks, labels=batch_tags)
        if params.n_gpu > 1 and params.multi_gpu:
            loss = loss.mean()
        loss_avg.update(loss.item())
        
        batch_output = model(batch_data, token_type_ids=None, attention_mask=batch_masks)  # shape: (batch_size, max_len, num_labels)
        
        batch_output = batch_output.detach().cpu().numpy()
        batch_tags = batch_tags.to('cpu').numpy()

        pred_tags.extend([idx2tag.get(idx) for indices in np.argmax(batch_output, axis=2) for idx in indices])
        true_tags.extend([idx2tag.get(idx) for indices in batch_tags for idx in indices])
    assert len(pred_tags) == len(true_tags)

    # logging loss, f1 and report
    metrics = {}
    f1 = f1_score(true_tags, pred_tags)
    metrics['loss'] = loss_avg()
    metrics['f1'] = f1
    metrics_str = "; ".join("{}: {:05.2f}".format(k, v) for k, v in metrics.items())
    logging.info("- {} metrics: ".format(mark) + metrics_str)

    if verbose:
        report = classification_report(true_tags, pred_tags)
        logging.info(report)
    return metrics


if __name__ == '__main__':
    args = parser.parse_args()

    # Load the parameters from json file
    json_path = os.path.join(args.model_dir, 'params.json')
    assert os.path.isfile(json_path), "No json configuration file found at {}".format(json_path)
    params = utils.Params(json_path)

    # Use GPUs if available
    params.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    params.n_gpu = torch.cuda.device_count()
    params.multi_gpu = args.multi_gpu

    # Set the random seed for reproducible experiments
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if params.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)  # set random seed for all GPUs
    params.seed = args.seed

    # Set the logger
    utils.set_logger(os.path.join(args.model_dir, 'evaluate.log'))

    # Create the input data pipeline
    logging.info("Loading the dataset...")

    # Initialize the DataLoader
    data_loader = DataLoader(args.data_dir, args.bert_model_dir, params, token_pad_idx=0)

    # Load data
    test_data = data_loader.load_data('test')

    # Specify the test set size
    params.test_size = test_data['size']
    params.eval_steps = params.test_size // params.batch_size
    test_data_iterator = data_loader.data_iterator(test_data, shuffle=False)

    logging.info("- done.")

    # Define the model
    #config_path = os.path.join(args.bert_model_dir, 'bert_config.json')
   # config = BertConfig.from_json_file(config_path)
    #model = BertForTokenClassification(config, num_labels=len(params.tag2idx))

    model.to(params.device)
    # Reload weights from the saved file
    utils.load_checkpoint(os.path.join(args.model_dir, args.restore_file + '.pth.tar'), model)
    if args.fp16:
        model.half()
    if params.n_gpu > 1 and args.multi_gpu:
        model = torch.nn.DataParallel(model)

    logging.info("Starting evaluation...")
    test_metrics = evaluate(model, test_data_iterator, params, mark='Test', verbose=True)

