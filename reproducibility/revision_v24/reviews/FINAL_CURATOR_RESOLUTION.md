Final curator resolution after actual Claude and Kimi reviews

Both reviewers were invoked through their real local Mac CLIs. Model identities, read calls, source hashes and outputs are preserved in the process logs. No new model fits were performed.

Claude accepted vertical Figure3, the integrated source-supervision Figure4 and the real Q-HERO ROC Figure5. Mean-absolute-error wording, frozen-source weights, independent target CatBoost fits and PNG600dpi were corrected. Kimi's layout suggestions and source/target boundary clarification are incorporated.

The last Claude review incorrectly treated a positive scaffold human−RF interval and a random-test interval containing zero as a contradiction. They are different evaluations. The main text now explicitly reports both conditional intervals: scaffold +0.110 [0.026,0.201], random [−0.066,0.297]. All contrasts remain in SI. This is a protocol-dependent result, without an assertion that the original published421-row test was beaten.

The proposed causal explanation for the local RF ROC dip was not established and was not inserted. The real curve remains unchanged. The optional frozen-source diagram clarification was implemented after review by replacing the existing footer with “Source encoders frozen · Five paired runs”; data and layouts were otherwise unchanged. Claude's log records the prior footer, not a new review of this final cosmetic edit. The final export was checked locally and the numerical validation rerun.

After the user's model-provenance question, local AST parsing confirmed text-embedding-3-small in recovered April/May code and exact identity of all four May CLASS_DESCRIPTIONS with the current task-embedding metadata. New cached vectors are4×1536 float32; requested/returned model names and SHA are verified. MainSection2.2 and SISectionS34 now specify the model and inputs. The unavailable historical vector cache is distinguished from the regenerated cache. This fact check required no further paid review.

Final document and numerical checks are recorded in document_validation.json, compact_roc_validation.json and task_text_embedding_provenance.json. Original v5 and all prior source documents are unchanged; original SI blocks, Office objects and numerical table cells are retained.
