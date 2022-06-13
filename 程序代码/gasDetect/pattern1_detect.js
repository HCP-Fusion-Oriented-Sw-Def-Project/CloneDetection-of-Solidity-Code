'use strict';
var parser = require("solidity-parser-antlr")
var fs = require('fs');
var path = require('path');

var Combinatorics = require('js-combinatorics');
var lodash = require('lodash');

var inputAddress = fs.readFileSync('/home/yfliu/paper_code/gasDetect/inputAddress').toString();
inputAddress = inputAddress.slice(0,inputAddress.length-1);
var outputAddress = '/home/yfliu/paper_data/gasPattern/gasDetectResult1.txt'
var filePath = path.resolve(inputAddress);
var countIndex = 0;
var countPattern1 = 0;
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

			// 解析智能合约
			var address = fileName.replace(/\.sol/g,"");
			var data = fs.readFileSync(filedir);
			var code = data.toString();
			var processedCode = code.replace(/&#39;/g,"\'");

			try{
				var result = parser.parse(processedCode,{loc : true});
			}catch(err){
    			console.error('Failed to parse, ' + address + '\n', err);
    			// fs.appendFileSync('/data/kongqp/gas2/log/compileFail.txt', ++countCompileFail + ' : ' + address + '\r\n');
    			return;
			}

			
			//fs.appendFileSync(outputAddress, countIndex + ' : ' + address + '\r\n');
			//flag = false;
			if(result.children.length != 0){
				for(var i = 0; i < result.children.length; i++){
					if(result.children[i].type == 'ContractDefinition'){
						fs.appendFileSync(outputAddress, countIndex + ' : ' + address + ' : ' + result.children[i].name + '\r\n');
						flag = false;
						// 变量重排
						var resultPattern1 = detectPattern1(result.children[i]);
						if(flag == true){
							fs.appendFileSync(outputAddress,"success" + '\r\n');
						}
					}
				}
			}
			/*
			if(flag == true){
				fs.appendFileSync(outputAddress,"success" + '\r\n');
			}
			fs.appendFileSync(outputAddress, "\n\n\n");*/
		});
	}
});

const permutator = (inputArr) => {
	let result = [];
  
	const permute = (arr, m = []) => {
	  if (arr.length === 0) {
		result.push(m)
	  } else {
		for (let i = 0; i < arr.length; i++) {
		  let curr = arr.slice();
		  let next = curr.splice(i, 1);
		  permute(curr.slice(), m.concat(next))
	   }
	 }
   }
  
   permute(inputArr)
  
   return result;
  }


function detectPattern1(_AST){
	global.identifiers= new Array();
	preOrderTraversel(_AST);



	var stateVariables = [];

	for(var i = 0; i < _AST.subNodes.length; i++){
		if(_AST.subNodes[i].type == 'StateVariableDeclaration'){
			switch(_AST.subNodes[i].variables[0].typeName.type){
				case 'ElementaryTypeName':
					stateVariables.push(_AST.subNodes[i].variables[0].typeName.name);
					fs.appendFileSync(outputAddress,  
						_AST.subNodes[i].variables[0].typeName.name + ' ' +  
						_AST.subNodes[i].variables[0].name + ' ' +  
						identifiers[_AST.subNodes[i].variables[0].name] + ':' +  
						_AST.subNodes[i].loc.start.line + "," + _AST.subNodes[i].loc.end.line +'\r\n');
					
					break; 
				case 'ArrayTypeName':
					stateVariables.push('array');
					
					fs.appendFileSync(outputAddress,  
						'array' + ' ' +  
						_AST.subNodes[i].variables[0].name + ' ' +  
						identifiers[_AST.subNodes[i].variables[0].name] + ':' +  
						_AST.subNodes[i].loc.start.line + "," + _AST.subNodes[i].loc.end.line +'\r\n');
					
					break; 
				case 'UserDefinedTypeName':
					stateVariables.push('UserDefined');
					
					fs.appendFileSync(outputAddress,  
						'UserDefined' + ' ' +  
						_AST.subNodes[i].variables[0].name + ' ' +  
						identifiers[_AST.subNodes[i].variables[0].name] + ':' +  
						_AST.subNodes[i].loc.start.line  + "," + _AST.subNodes[i].loc.end.line +'\r\n');
					
					break; 
				case 'Mapping':
					stateVariables.push('Mapping');
					fs.appendFileSync(outputAddress,  
						'Mapping' + ' ' +  
						_AST.subNodes[i].variables[0].name + ' ' +  
						identifiers[_AST.subNodes[i].variables[0].name] + ':' +  
						_AST.subNodes[i].loc.start.line  + "," + _AST.subNodes[i].loc.end.line +'\r\n');
					break; 
				case 'FunctionTypeName':
					console.log("Error pattern 1_1");
					break; 
				case 'ImportDirective':
					console.log("Error pattern 1_2");
					break; 
				default:
					console.log("Error pattern 1_3");
			}

		}
	}

	if(stateVariables.length == 0){
		fs.appendFileSync(outputAddress, "stateVariables.length == 0" + '\r\n');
		return false;
	}

	var stateVariablesEquit256 = [];
	var tempStateVariablesLess256 = [];
	for(var i = 0; i < stateVariables.length; i++){
		var tempSize = getSize(stateVariables[i]);
		switch(tempSize){
			case 256:
				stateVariablesEquit256.push(stateVariables[i]);
				break;
			case -400 :
				fs.appendFileSync(outputAddress, "Error : " + stateVariables[i] + '\r\n');
				break;
			default:
				tempStateVariablesLess256.push(stateVariables[i]);
		}
	}

	if(tempStateVariablesLess256.length > 7){
		fs.appendFileSync(outputAddress, "tempStateVariablesLess256.length > 7" + '\r\n');
		return false;
	}
	
	var tempBestOrder = [];
	var tempMinSlot = getNumSlot(stateVariables);
	//fs.appendFileSync(outputAddress, "original : " + tempMinSlot + " slot(s)"+ '\r\n')

	if(tempMinSlot != -400 && tempStateVariablesLess256.length > 1){
		fs.appendFileSync('/home/yfliu/printJS1',tempStateVariablesLess256.toString())
		var cmb = permutator(tempStateVariablesLess256);
		var permutation = cmb;
		var uniqPermutation = lodash.uniqWith(permutation, lodash.isEqual)
		var tempBasicCost = stateVariablesEquit256.length;
		for(var i = 0; i < uniqPermutation.length; i++){
			var tempCost = getNumSlot(uniqPermutation[i]) + tempBasicCost;
			if(tempCost > 0 && tempCost < tempMinSlot){
				tempBestOrder = uniqPermutation[i].concat(stateVariablesEquit256);
				tempMinSlot = tempCost;
			}
		}
	}
	if( tempMinSlot < getNumSlot(stateVariables)){
		/*
		fs.appendFileSync(outputAddress, "optimization : " + tempMinSlot + " slot(s)"+ '\r\n');
		fs.appendFileSync(outputAddress, "optimization order : " + '\r\n');
		for(var i = 0; i < tempBestOrder.length; i++){
			fs.appendFileSync(outputAddress,  tempBestOrder[i] + '\r\n');
		}
		*/
		flag = true;
		return true;
	}else{
		return false;
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
			if(_AST.type == 'Identifier'){
				if(global.identifiers.hasOwnProperty(_AST.name)){
					global.identifiers[_AST.name] += 1;
				}else{
					global.identifiers[_AST.name]  = 1;
				}
			}
		}
	}
	for(var key in _AST){
		preOrderTraversel(_AST[key]);	
	}
}



function getNumSlot(_stateVariables){
	var numSlot = 0;
	var tempSlotCost = 0;
	for(var i = 0; i < _stateVariables.length; i++){
		var tempSize = getSize(_stateVariables[i]);
		if(tempSize != -400){
			if(tempSize + tempSlotCost > 256){
				numSlot++ ;
				tempSlotCost = tempSize;
			}else{
				tempSlotCost += tempSize;
			}
		}else{
			return -400;
		}
	}
	if(tempSlotCost != 0){
		numSlot++ ;
	}
	return numSlot;
}

function getSize(_variableType){
	switch(_variableType){
		case 'bool':
			return 8;
		case 'byte':
			return 8;
		case 'address':
			return 160;
		case 'string':
			return 256;
		case 'bytes':
			return 256;
		case 'array':
			return 256;
		case 'UserDefined':
			return 256;
		case 'Mapping':
			return 256;
		case 'uint':
			return 256;
		case 'int':
			return 256;
		case 'bytes':
			return 256;
	}

	if(_variableType.indexOf("int") != -1 ){
		return parseInt(_variableType.replace(/int/g,"").replace(/u/g,""));
	}

	if(_variableType.indexOf("bytes") != -1 ){
		return parseInt(_variableType.replace(/bytes/g,""))*8;
	}

	return -400;
}
