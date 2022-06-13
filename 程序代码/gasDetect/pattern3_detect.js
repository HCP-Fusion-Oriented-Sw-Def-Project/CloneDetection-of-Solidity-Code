'use strict';
var parser = require("solidity-parser-antlr")
var fs = require('fs');
var path = require('path');
var inputAddress = fs.readFileSync('/home/yfliu/paper_code/gasDetect/inputAddress').toString();
inputAddress = inputAddress.slice(0,inputAddress.length-1);
var outputAddress = '/home/yfliu/paper_data/gasPattern/gasDetectResult3.txt'
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
    			return;
			}


			//fs.appendFileSync(outputAddress, countIndex + ' : ' + address + '\r\n');
			//flag = false;
			if(result.children.length != 0){
				for(var i = 0; i < result.children.length; i++){
					if(result.children[i].type == 'ContractDefinition'){
						// 循环中重复访问state变量
						fs.appendFileSync(outputAddress, countIndex + ' : ' + address + ' : ' + result.children[i].name + '\r\n');
						flag = false;
						detectPattern(result.children[i]);
						if(flag == true){
							fs.appendFileSync(outputAddress,"success" + '\r\n');
						}
					}
				}
			}

		});
	}
});


function detectPattern(_AST){
	// 搜集所有普通（非数组）state变量的变量名
	global.stateVariableNamesWithoutArray = [];

	for(var i = 0; i < _AST.subNodes.length; i++){
		if(_AST.subNodes[i].type == 'StateVariableDeclaration'){

			if(_AST.subNodes[i].variables[0].isDeclaredConst == true){
				continue;
			}

			if(_AST.subNodes[i].variables[0].typeName.type == 'ElementaryTypeName'){
				stateVariableNamesWithoutArray.push(_AST.subNodes[i].variables[0].name);
				//fs.appendFileSync(outputAddress,  "-0 : " + _AST.subNodes[i].variables[0].name + " : " + _AST.subNodes[i].variables[0].typeName.name + '\r\n');
			}
		}
	}
	// 检查循环内是否对其赋值或访问
	if(stateVariableNamesWithoutArray.length != 0){
		for(var i = 0; i < _AST.subNodes.length; i++){
			if(_AST.subNodes[i].type == 'FunctionDefinition'){
				if(_AST.subNodes[i].stateMutability != null){
					if(["constant", "view", "pure"].indexOf(_AST.subNodes[i].stateMutability) != -1){
						continue;
					}
				}
				preOrderTraversel(_AST.subNodes[i]);
			}
		}
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
			if(_AST.type == 'ForStatement' || _AST.type == 'WhileStatement' || _AST.type == 'DoWhileStatement'){
				//fs.appendFileSync(outputAddress, "-1 : " + _AST.loc.start.line + ", " + _AST.loc.end.line + '\r\n');
				checkStateVariable(_AST.body);
			}
		}
	}
	for(var key in _AST){
		preOrderTraversel(_AST[key]);	
	}
}


function checkStateVariable(_AST){
	if(typeof _AST == 'string' || typeof _AST == 'number' || _AST == null){
		return;
	}
	if(_AST instanceof Array){
		// console.log();
	}else{
		if(_AST.hasOwnProperty('type')){
			if(_AST.type == 'Identifier'){
				if(stateVariableNamesWithoutArray.indexOf(_AST.name) != -1){
					fs.appendFileSync(outputAddress, _AST.name + " : " + _AST.loc.start.line + ", " + _AST.loc.end.line + '\r\n');
					flag = true;
				}
			}
		}
	}
	for(var key in _AST){
		checkStateVariable(_AST[key]);	
	}
}