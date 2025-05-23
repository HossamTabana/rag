from fastapi import FastAPI, APIRouter,status,Request
from fastapi.responses import JSONResponse
from routes.Schemes.nlp import PushRequest ,SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.enums.ResponseEnum import ResponseSignal
from controllers import NLPController
import os 
import logging
from typing import List


logger =logging.getLogger('uvcorn.error')


nlp_router = APIRouter(
    prefix ="/api/v1/nlp",
    tags =["api_v1/","nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request :Request ,project_id :int ,Push_request : PushRequest):
    
    
    project_model = await ProjectModel.create_instance( 
        db_client = request.app.db_client
        
    )
    
    project =await project_model.get_project_or_create_one(
        project_id = project_id
    )
    
    chunk_model = await ChunkModel.create_instance(
        db_client = request.app.db_client
        
    )
    
    
    
    if not project:
        return JSONResponse(
            status_code =status.HTTP_400_BAD_REQUEST,
            
            content ={
                
                "Signal":ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            },
              
        )
    
    
    nlp_controller = NLPController(
        VectorDB_client = request.app.VectorDB_client,
        Generation_client = request.app.Generation_client,
        Embedding_Client = request.app.Embedding_Client,
        template_parser = request.app.template_parser,
        
        
    )
    
    
    has_records =True
   
    page_no =1 
    
    inserted_items_count =0
    
    idx =0
    
    while has_records :
    
        page_chunks =await chunk_model.get_project_chunks(project_id = project.project_id,
                                                          page_no = page_no)
        
        if len(page_chunks):
            page_no +=1

        if not page_chunks or len(page_chunks) == 0:
            has_records =False
            break
        
        chunks_ids = list(range(idx , idx +len(page_chunks)))
        
        idx += len(page_chunks)
        
        # check values
        # print(f"this  project :{project}")
        # print(f"this number for do_reset :{Push_request.do_reset}")
        # print(f"this list for chunks_ids :{chunks_ids}")
        # print(f"this number for length page_chunks :{len(page_chunks)}")
        # print(f"this is the content of :{page_chunks}")
        
        is_inserted=nlp_controller.index_into_vector_db(
            project = project ,
            chunks= page_chunks,
            do_reset = Push_request.do_reset,
            chunks_ids = chunks_ids
            )
        
    
    
        if not is_inserted :
            return JSONResponse(
            status_code =status.HTTP_400_BAD_REQUEST,
            
            content ={
                
                "signal":ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
            },
              
        )
            
        inserted_items_count += len(page_chunks)
        
    
    return JSONResponse(
        
        content ={
            
            "signal" : ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count" : inserted_items_count
            
        }
    )
    
@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request :Request ,project_id :int):
    
    
    project_model = await ProjectModel.create_instance( 
        db_client = request.app.db_client
        
    )
    
    project =await project_model.get_project_or_create_one(
        project_id = project_id
    )
    
    
    nlp_controller = NLPController(
        VectorDB_client = request.app.VectorDB_client,
        Generation_client = request.app.Generation_client,
        Embedding_Client = request.app.Embedding_Client,
        template_parser = request.app.template_parser,
        
    )
    
    collection_info = nlp_controller.get_vector_db_collection_info(
        
        project = project
    )
    
    return JSONResponse(
        
        content ={
            
            "Signal" : ResponseSignal.VECTORDB_COLLECTION_RETRIVED.value,
            "collection_info" : collection_info
            
        }
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(request :Request ,project_id :int ,search_request :SearchRequest):
    
    project_model = await ProjectModel.create_instance( 
        db_client = request.app.db_client
        
    )
    
    project =await project_model.get_project_or_create_one(
        project_id = project_id
    )
    
    nlp_controller = NLPController(
        VectorDB_client = request.app.VectorDB_client,
        Generation_client = request.app.Generation_client,
        Embedding_Client = request.app.Embedding_Client,
        template_parser = request.app.template_parser,
        
        
    )
    # check the values:
    # print(f"this  project :{project}")
    # print(f"this is the Query from user :{search_request.text}")
    # print(f"this is limit :{search_request.limit}")
    

    results = nlp_controller.search_vector_db_collection(
        
        project =project,
        text = search_request.text,
        limit = search_request.limit
    )
    
    #print(f"this is the results:{results}")
    
    if not results :
        return JSONResponse(
            status_code =status.HTTP_400_BAD_REQUEST,
            
            content ={
                
                "signal":ResponseSignal.VECTORDB_SEARCH_ERROR.value
            },
              
        ) 
    
    return JSONResponse(
        
        content ={
            
            "Signal" : ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": [result.dict() for result in results]

            
        }
    )


@nlp_router.post("/index/answer/{project_id}")
async def search_index(request :Request ,project_id : int ,search_request :SearchRequest):
    
    project_model = await ProjectModel.create_instance( 
        db_client = request.app.db_client
        
    )
    
    project =await project_model.get_project_or_create_one(
        project_id = project_id
    )
    
    nlp_controller = NLPController(
        VectorDB_client = request.app.VectorDB_client,
        Generation_client = request.app.Generation_client,
        Embedding_Client = request.app.Embedding_Client,
        template_parser = request.app.template_parser,
        
        
     )
    
    answer ,full_prompt , chat_history = nlp_controller.answer_rag_quesion(
                    project =project,
                    Query = search_request.text,
                    limit = search_request.limit
            )
    
    if not answer:
        return JSONResponse(
            status_code =status.HTTP_400_BAD_REQUEST,
            
            content ={
                
                "signal":ResponseSignal.GENERATE_ANSWER_ERROR.value
            },
              
        )
    
    return JSONResponse(
        
        content ={
            "Signal" : ResponseSignal.GENERATE_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt" : full_prompt,
            "chat_history" :chat_history,
            
        }
    )
    
    
    
 
    
    
    
    
    
    
              
            
        
    
    



