'use strict';
var parser = require("solidity-parser-antlr")
var fs = require('fs');
var path = require('path');

var inputAddress = fs.readFileSync('/home/yfliu/paper_code/gasDetect/inputAddress').toString();
inputAddress = inputAddress.slice(0,inputAddress.length-1);
var outputAddress = '/home/yfliu/paper_data/gasPattern/gasDetectResult7.txt'
var filePath = path.resolve(inputAddress);
var countIndex = 0;
var countCompileFail = 0;
var flag = false;

fs.readdir(filePath,function(err,files){
	if(err){
		console.warn(err)
	}else{
		files.forEach(function(fileName){
			console.log("正在处理第 " + ++countIndex + " 个文件 : " + fileName);
			
			// 读取智能合约
			var filedir = path.join(filePath,fileName);
			if (fileName.search(":") != -1){
				return;
			}
			// 解析智能合约
			var address = fileName.replace(/\.sol/g,"");
			var data = fs.readFileSync(filedir);
			var code = data.toString();
			var processedCode = code.replace(/&#39;/g,"\'");

			try{
				var result = parser.parse(processedCode,{loc : true});
			}catch(err){
    			console.error('Failed to parse, ' + address + '\n', err);
    			// fs.appendFileSync('/data/kongqp/gas_optimization/log/compileFail.txt', ++countCompileFail + ' : ' + address + '\r\n');
    			return;
			}


			// fs.appendFileSync(outputAddress, countIndex + ' : ' + address + '\r\n');
			// flag = false;
			if(result.children.length != 0){
				for(var i = 0; i < result.children.length; i++){
					if(result.children[i].type == 'ContractDefinition'){
						fs.appendFileSync(outputAddress, countIndex + ' : ' + address + ' : ' + result.children[i].name + '\r\n');
						flag = false;
						// 如果函数不涉及内部调用，public 改 external
						detectPattern(result.children[i]);
						if(flag == true){
							fs.appendFileSync(outputAddress,"success" + '\r\n');
						}
					}
				}
			}
			// if(flag == true){
			// 	fs.appendFileSync(outputAddress,"success" + '\r\n');
			// }
		});
	}
});


function detectPattern(_AST){
	
	// 收集输入参数包含数组)及可见性为public的函数
	global.function_names_dict= new Array();

	for(var i = 0; i < _AST.subNodes.length; i++){
		if(_AST.subNodes[i].type == 'FunctionDefinition'){
			if(_AST.subNodes[i].visibility != null){
				if(_AST.subNodes[i].visibility != 'public'){
					continue;
				}
			}
			if(_AST.subNodes[i].isConstructor){
				continue;
			}

			if(_AST.subNodes[i].parameters.length != 0){
				for(var j=0; j < _AST.subNodes[i].parameters.length; j++){
					if(_AST.subNodes[i].parameters[j].type == 'VariableDeclaration'){
						if(_AST.subNodes[i].parameters[j].typeName.type == 'ArrayTypeName'){
							function_names_dict[_AST.subNodes[i].name] =_AST.subNodes[i].parameters[j].loc.start.line + ',' + _AST.subNodes[i].parameters[j].loc.end.line;
							break;
						}
					}
				}
			}
		}
	}

	// 去除被内部调用的函数
	preOrderTraversel(_AST);

	//打印需要public转external的函数
	for(var key in function_names_dict){
		fs.appendFileSync(outputAddress, key + " : " + function_names_dict[key] + '\r\n');
		flag = true;
	}
}

function preOrderTraversel(_AST){
	if(typeof _AST == 'string' || typeof _AST == 'number' || _AST == null){
		return;
	}
	if(_AST instanceof Array){
		// console.log();
	}else{
		if(_AST.hasOwnProperty('type')){
			if(_AST.type == 'FunctionCall'){
				if(_AST.expression != null){
					if(_AST.expression.type == 'Identifier'){
						try{
							delete function_names_dict[_AST.expression.name];
						}catch(err){
    						fs.appendFileSync(outputAddress, "Error delete : " + _AST.expression.name + '\r\n');
						}
					}
				}
			}
		}
	}
	for(var key in _AST){
		preOrderTraversel(_AST[key]);	
	}
}